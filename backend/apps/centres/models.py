from django.db import models


class Centre(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=32, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"
