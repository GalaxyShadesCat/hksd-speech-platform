from django.core.exceptions import ValidationError
from django.db import models


class SoundGroup(models.TextChoices):
    INITIAL = "INITIAL", "Initial consonant"
    FINAL = "FINAL", "Final consonant"
    VOWEL = "VOWEL", "Vowel"
    DIPHTHONG = "DIPHTHONG", "Diphthong"
    OTHER = "OTHER", "Other"


class Word(models.Model):
    hanzi = models.CharField(max_length=20, blank=True)
    jyutping = models.CharField(max_length=50, blank=True)
    meaning = models.CharField(max_length=200, blank=True)

    image_url = models.URLField(blank=True)
    audio_url = models.URLField(blank=True)

    sound_group = models.CharField(max_length=16, choices=SoundGroup.choices, default=SoundGroup.OTHER)
    hierarchy_stage = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hanzi or self.jyutping or f"Word {self.pk}"


class WordComponent(models.Model):
    parent_word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="components")
    component_word = models.ForeignKey(Word, on_delete=models.PROTECT, related_name="used_in")
    position = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["parent_word", "position"], name="uniq_wordcomponent_parent_position"),
        ]
        ordering = ["position"]

    def _creates_cycle(self):
        visited = set()
        stack = [self.component_word_id]
        target = self.parent_word_id

        while stack:
            current = stack.pop()
            if current == target:
                return True
            if current in visited:
                continue
            visited.add(current)
            next_ids = WordComponent.objects.filter(parent_word_id=current).values_list("component_word_id", flat=True)
            stack.extend(next_ids)
        return False

    def clean(self):
        super().clean()
        if self.parent_word_id == self.component_word_id:
            raise ValidationError("A word cannot be a component of itself.")
        if self.parent_word_id and self.component_word_id and self._creates_cycle():
            raise ValidationError("This component would create a cycle in the word graph.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent_word_id} <- {self.component_word_id} ({self.position})"
