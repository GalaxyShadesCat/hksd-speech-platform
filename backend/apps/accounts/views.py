from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.practice.models import PracticeSession
from apps.screening.models import ScreeningSession

from .models import PasswordResetLink, UserProfile, UserRole
from .permissions import IsStaffOrAdmin
from .serializers import (
    CentreSelectionSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Registration successful. Please log in."}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class MeCentreView(APIView):
    def put(self, request):
        serializer = CentreSelectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = request.user.profile
        profile.centre = serializer.validated_data["centre"]
        profile.save(update_fields=["centre"])

        return Response({"detail": "Centre updated."})


class StaffPasswordResetView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        try:
            target_user = User.objects.select_related("profile").get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        requester_profile = request.user.profile
        target_profile = getattr(target_user, "profile", None)

        if not request.user.is_superuser:
            if requester_profile.role not in {UserRole.STAFF, UserRole.ADMIN}:
                return Response({"detail": "You do not have permission."}, status=status.HTTP_403_FORBIDDEN)
            if not target_profile or target_profile.role != UserRole.PARENT:
                return Response({"detail": "You may only reset parent accounts."}, status=status.HTTP_400_BAD_REQUEST)
            if requester_profile.centre_id != target_profile.centre_id:
                return Response({"detail": "User is outside your centre."}, status=status.HTTP_403_FORBIDDEN)

        uidb64 = urlsafe_base64_encode(force_bytes(target_user.pk))
        token = default_token_generator.make_token(target_user)

        reset_link = PasswordResetLink.objects.create(
            user=target_user,
            created_by=request.user,
            uidb64=uidb64,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/reset-password/{reset_link.uidb64}/{reset_link.token}/"
        return Response({"reset_url": url, "expires_at": reset_link.expires_at})


class StaffParentsView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        centre_id = request.query_params.get("centre_id")
        profile = request.user.profile

        queryset = UserProfile.objects.filter(role=UserRole.PARENT).select_related("user", "centre")
        if request.user.is_superuser:
            if centre_id:
                queryset = queryset.filter(centre_id=centre_id)
        else:
            queryset = queryset.filter(centre_id=profile.centre_id)
            if centre_id:
                queryset = queryset.filter(centre_id=centre_id)

        data = [
            {
                "user_id": p.user_id,
                "username": p.user.username,
                "centre_id": p.centre_id,
                "centre_name": p.centre.name if p.centre else None,
            }
            for p in queryset.order_by("user__username")
        ]
        return Response(data)


class StaffParentSessionsView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request, parent_id):
        days = int(request.query_params.get("days", 30))
        since = timezone.now() - timedelta(days=days)

        try:
            parent = User.objects.select_related("profile").get(pk=parent_id)
        except User.DoesNotExist:
            return Response({"detail": "Parent not found."}, status=status.HTTP_404_NOT_FOUND)

        requester = request.user
        if not requester.is_superuser:
            requester_centre = requester.profile.centre_id
            if getattr(parent.profile, "centre_id", None) != requester_centre:
                return Response({"detail": "Parent is outside your centre."}, status=status.HTTP_403_FORBIDDEN)

        practice_sessions = PracticeSession.objects.filter(created_by=parent, started_at__gte=since)
        screening_sessions = ScreeningSession.objects.filter(created_by=parent, started_at__gte=since)

        return Response(
            {
                "parent_id": parent.id,
                "username": parent.username,
                "practice_sessions": [
                    {
                        "id": s.id,
                        "session_type": s.session_type,
                        "started_at": s.started_at,
                        "submitted_at": s.submitted_at,
                    }
                    for s in practice_sessions.order_by("-started_at")
                ],
                "screening_sessions": [
                    {
                        "id": s.id,
                        "age_band": s.age_band.label,
                        "started_at": s.started_at,
                        "submitted_at": s.submitted_at,
                    }
                    for s in screening_sessions.select_related("age_band").order_by("-started_at")
                ],
            }
        )


class StaffAggregateMissedView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request, centre_id):
        days = int(request.query_params.get("days", 30))
        since = timezone.now() - timedelta(days=days)

        requester = request.user
        if not requester.is_superuser and requester.profile.centre_id != centre_id:
            return Response({"detail": "You do not have access to this centre."}, status=status.HTTP_403_FORBIDDEN)

        practice_attempts = (
            PracticeSession.objects.filter(centre_id=centre_id, started_at__gte=since)
            .values("attempts__word_id", "attempts__word__hanzi", "attempts__word__jyutping")
            .annotate(missed=Count("attempts", filter=Q(attempts__is_correct=False)))
            .filter(missed__gt=0)
            .order_by("-missed")
        )

        data = [
            {
                "word_id": row["attempts__word_id"],
                "hanzi": row["attempts__word__hanzi"],
                "jyutping": row["attempts__word__jyutping"],
                "missed_count": row["missed"],
            }
            for row in practice_attempts
        ]
        return Response({"centre_id": centre_id, "days": days, "results": data})
