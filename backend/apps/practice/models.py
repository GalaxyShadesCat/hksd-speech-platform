from django.conf import settings
from django.db import models

from apps.centres.models import Centre
from apps.lexicon.models import Word


class PracticeSessionType(models.TextChoices):
    DAILY = "DAILY", "Daily practice"
    REVIEW = "REVIEW", "Review practice"
    SCREENING = "SCREENING", "Screening"


class PracticeSession(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    centre = models.ForeignKey(Centre, null=True, blank=True, on_delete=models.SET_NULL)

    session_type = models.CharField(max_length=16, choices=PracticeSessionType.choices, default=PracticeSessionType.DAILY)
    child_display_name = models.CharField(max_length=100, blank=True)
    planned_item_count = models.PositiveSmallIntegerField(default=10)

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.session_type} {self.id}"


class PracticeItem(models.Model):
    session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, related_name="items")
    word = models.ForeignKey(Word, on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "position"], name="uniq_practiceitem_session_position"),
        ]
        ordering = ["position"]


class PracticeAttempt(models.Model):
    session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, related_name="attempts")
    word = models.ForeignKey(Word, on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "position"], name="uniq_practiceattempt_session_position"),
        ]
        ordering = ["position"]
