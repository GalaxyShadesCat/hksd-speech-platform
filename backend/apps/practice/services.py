from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.lexicon.models import Word

from .models import PracticeAttempt


def select_daily_words(limit=10):
    queryset = Word.objects.filter(is_active=True).order_by("hierarchy_stage", "id")
    return list(queryset[:limit])


def recent_missed_words_for_user(user, days=30, limit=10):
    since = timezone.now() - timedelta(days=days)
    missed = (
        PracticeAttempt.objects.filter(session__created_by=user, session__started_at__gte=since, is_correct=False)
        .values("word_id")
        .annotate(missed_count=Count("id"))
        .order_by("-missed_count")
    )

    word_ids = [row["word_id"] for row in missed[:limit]]
    words = Word.objects.in_bulk(word_ids)
    return [words[word_id] for word_id in word_ids if word_id in words]


def aggregate_missed_words_for_user(user, days=30):
    since = timezone.now() - timedelta(days=days)
    return (
        PracticeAttempt.objects.filter(session__created_by=user, session__started_at__gte=since, is_correct=False)
        .values("word_id", "word__hanzi", "word__jyutping")
        .annotate(missed_count=Count("id"), total_attempts=Count("id", filter=Q(is_correct=False) | Q(is_correct=True)))
        .order_by("-missed_count")
    )
