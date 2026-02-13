from django.conf import settings
from django.db import models

from apps.centres.models import Centre
from apps.lexicon.models import Word


class AgeBand(models.Model):
    label = models.CharField(max_length=50, unique=True)
    min_months = models.PositiveSmallIntegerField()
    max_months = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.label


class ScreeningSet(models.Model):
    name = models.CharField(max_length=200)
    age_band = models.ForeignKey(AgeBand, on_delete=models.PROTECT)
    centre = models.ForeignKey(Centre, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.age_band})"


class ScreeningItem(models.Model):
    screening_set = models.ForeignKey(ScreeningSet, on_delete=models.CASCADE, related_name="items")
    word = models.ForeignKey(Word, on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["screening_set", "position"], name="uniq_screeningitem_set_position"),
        ]
        ordering = ["position"]


class ScreeningSession(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    centre = models.ForeignKey(Centre, null=True, blank=True, on_delete=models.SET_NULL)
    age_band = models.ForeignKey(AgeBand, on_delete=models.PROTECT)
    screening_set = models.ForeignKey(ScreeningSet, on_delete=models.PROTECT)

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Screening {self.id} ({self.age_band})"


class ScreeningAttempt(models.Model):
    session = models.ForeignKey(ScreeningSession, on_delete=models.CASCADE, related_name="attempts")
    word = models.ForeignKey(Word, on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "position"], name="uniq_screeningattempt_session_position"),
        ]
        ordering = ["position"]
