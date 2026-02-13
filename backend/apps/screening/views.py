from collections import Counter

from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lexicon.models import Word

from .models import AgeBand, ScreeningAttempt, ScreeningSession, ScreeningSet
from .serializers import AgeBandSerializer, ScreeningSessionSerializer


class AgeBandListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bands = AgeBand.objects.filter(is_active=True).order_by("min_months", "max_months")
        return Response(AgeBandSerializer(bands, many=True).data)


class ScreeningSessionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        age_band_id = request.data.get("age_band_id")
        if not age_band_id:
            return Response({"detail": "age_band_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            age_band = AgeBand.objects.get(pk=age_band_id, is_active=True)
        except AgeBand.DoesNotExist:
            return Response({"detail": "Age band not found."}, status=status.HTTP_404_NOT_FOUND)

        centre_id = getattr(request.user.profile, "centre_id", None)

        screening_set = (
            ScreeningSet.objects.filter(age_band=age_band, is_active=True, centre_id=centre_id).first()
            or ScreeningSet.objects.filter(age_band=age_band, is_active=True, centre__isnull=True).first()
        )
        if not screening_set:
            return Response({"detail": "No active screening set available."}, status=status.HTTP_400_BAD_REQUEST)

        if not screening_set.items.exists():
            return Response({"detail": "Screening set has no items."}, status=status.HTTP_400_BAD_REQUEST)

        session = ScreeningSession.objects.create(
            created_by=request.user,
            centre_id=centre_id,
            age_band=age_band,
            screening_set=screening_set,
        )
        return Response({"id": session.id}, status=status.HTTP_201_CREATED)


class ScreeningSessionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = ScreeningSession.objects.select_related("age_band", "created_by", "screening_set").get(pk=session_id)
        except ScreeningSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.created_by_id != request.user.id:
            return Response({"detail": "You do not have access to this session."}, status=status.HTTP_403_FORBIDDEN)

        return Response(ScreeningSessionSerializer(session).data)


class ScreeningSessionSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, session_id):
        try:
            session = ScreeningSession.objects.select_related("screening_set", "created_by").get(pk=session_id)
        except ScreeningSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.created_by_id != request.user.id:
            return Response({"detail": "You do not have access to this session."}, status=status.HTTP_403_FORBIDDEN)
        if session.submitted_at:
            return Response({"detail": "Session has already been submitted."}, status=status.HTTP_400_BAD_REQUEST)

        answers = request.data.get("answers", [])
        expected_items = list(session.screening_set.items.select_related("word").order_by("position"))
        expected_positions = {item.position for item in expected_items}
        answer_map = {entry.get("position"): entry for entry in answers}

        if set(answer_map.keys()) != expected_positions:
            return Response(
                {"detail": "All positions must be answered exactly once."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attempts = []
        for item in expected_items:
            answer = answer_map[item.position]
            if "is_correct" not in answer:
                return Response({"detail": f"Missing is_correct for position {item.position}."}, status=status.HTTP_400_BAD_REQUEST)
            attempts.append(
                ScreeningAttempt(
                    session=session,
                    word=item.word,
                    position=item.position,
                    is_correct=bool(answer["is_correct"]),
                )
            )

        ScreeningAttempt.objects.bulk_create(attempts)
        session.submitted_at = timezone.now()
        session.save(update_fields=["submitted_at"])

        return Response({"detail": "Screening submitted."})


class ScreeningSessionSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = ScreeningSession.objects.get(pk=session_id, created_by=request.user)
        except ScreeningSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        attempts = session.attempts.select_related("word").order_by("position")
        missed = [attempt for attempt in attempts if not attempt.is_correct]

        missed_words = [
            {
                "position": attempt.position,
                "word_id": attempt.word_id,
                "hanzi": attempt.word.hanzi,
                "jyutping": attempt.word.jyutping,
                "sound_group": attempt.word.sound_group,
            }
            for attempt in missed
        ]

        sound_counts = Counter([attempt.word.sound_group for attempt in missed])
        recommended = [
            {"sound_group": sound_group, "count": count}
            for sound_group, count in sound_counts.most_common(3)
        ]

        return Response(
            {
                "session_id": session.id,
                "missed_words": missed_words,
                "missed_sound_group_counts": sound_counts,
                "recommended_focus": recommended,
            }
        )
