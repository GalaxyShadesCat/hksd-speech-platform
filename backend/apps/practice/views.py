from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PracticeAttempt, PracticeItem, PracticeSession, PracticeSessionType
from .serializers import PracticeSessionSerializer
from .services import aggregate_missed_words_for_user, recent_missed_words_for_user, select_daily_words


class PracticeSessionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        planned_item_count = int(request.data.get("planned_item_count", 10))
        child_display_name = request.data.get("child_display_name", "")

        words = select_daily_words(limit=planned_item_count)
        if not words:
            return Response({"detail": "No active words are available."}, status=status.HTTP_400_BAD_REQUEST)

        session = PracticeSession.objects.create(
            created_by=request.user,
            centre_id=getattr(request.user.profile, "centre_id", None),
            session_type=PracticeSessionType.DAILY,
            child_display_name=child_display_name,
            planned_item_count=planned_item_count,
        )

        items = [
            PracticeItem(session=session, word=word, position=index)
            for index, word in enumerate(words, start=1)
        ]
        PracticeItem.objects.bulk_create(items)

        return Response({"id": session.id}, status=status.HTTP_201_CREATED)


class PracticeSessionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = PracticeSession.objects.prefetch_related("items__word").get(pk=session_id)
        except PracticeSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.created_by_id != request.user.id:
            return Response({"detail": "You do not have access to this session."}, status=status.HTTP_403_FORBIDDEN)

        return Response(PracticeSessionSerializer(session).data)


class PracticeSessionSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, session_id):
        try:
            session = PracticeSession.objects.prefetch_related("items__word").get(pk=session_id)
        except PracticeSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.created_by_id != request.user.id:
            return Response({"detail": "You do not have access to this session."}, status=status.HTTP_403_FORBIDDEN)
        if session.submitted_at:
            return Response({"detail": "Session has already been submitted."}, status=status.HTTP_400_BAD_REQUEST)

        answers = request.data.get("answers", [])
        answer_map = {entry.get("position"): entry for entry in answers}
        expected_items = list(session.items.all().order_by("position"))
        expected_positions = {item.position for item in expected_items}

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
                PracticeAttempt(
                    session=session,
                    word=item.word,
                    position=item.position,
                    is_correct=bool(answer["is_correct"]),
                )
            )
        PracticeAttempt.objects.bulk_create(attempts)

        session.submitted_at = timezone.now()
        session.save(update_fields=["submitted_at"])

        missed = [attempt for attempt in attempts if not attempt.is_correct]
        score = len(attempts) - len(missed)

        return Response(
            {
                "detail": "Great effort, keep practising.",
                "score": {"correct": score, "total": len(attempts)},
                "missed": [
                    {
                        "position": attempt.position,
                        "word_id": attempt.word_id,
                        "hanzi": attempt.word.hanzi,
                        "jyutping": attempt.word.jyutping,
                    }
                    for attempt in missed
                ],
            }
        )


class PracticeHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sessions = PracticeSession.objects.filter(created_by=request.user).order_by("-started_at")
        data = [
            {
                "id": session.id,
                "session_type": session.session_type,
                "started_at": session.started_at,
                "submitted_at": session.submitted_at,
            }
            for session in sessions
        ]
        return Response(data)


class PracticeMissedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        rows = aggregate_missed_words_for_user(request.user, days=days)
        data = [
            {
                "word_id": row["word_id"],
                "hanzi": row["word__hanzi"],
                "jyutping": row["word__jyutping"],
                "missed_count": row["missed_count"],
            }
            for row in rows
        ]
        return Response({"days": days, "results": data})


class PracticeReviewCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        days = int(request.data.get("days", 30))
        limit = int(request.data.get("planned_item_count", 10))
        words = recent_missed_words_for_user(request.user, days=days, limit=limit)

        if not words:
            return Response({"detail": "No missed items available for review."}, status=status.HTTP_400_BAD_REQUEST)

        session = PracticeSession.objects.create(
            created_by=request.user,
            centre_id=getattr(request.user.profile, "centre_id", None),
            session_type=PracticeSessionType.REVIEW,
            planned_item_count=len(words),
            child_display_name=request.data.get("child_display_name", ""),
        )

        PracticeItem.objects.bulk_create(
            [PracticeItem(session=session, word=word, position=index) for index, word in enumerate(words, start=1)]
        )

        return Response({"id": session.id}, status=status.HTTP_201_CREATED)
