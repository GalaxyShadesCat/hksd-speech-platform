from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.centres.models import Centre


class UserRole(models.TextChoices):
    PARENT = "PARENT", "Parent"
    STAFF = "STAFF", "Staff"
    ADMIN = "ADMIN", "Admin"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=16, choices=UserRole.choices, default=UserRole.PARENT)
    centre = models.ForeignKey(Centre, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.role in {UserRole.STAFF, UserRole.ADMIN} and self.centre_id is None:
            raise ValidationError("Staff and admin profiles must have a centre.")

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class PasswordResetLink(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="issued_password_resets",
    )
    token = models.CharField(max_length=255)
    uidb64 = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def default_expiry(cls):
        return timezone.now() + timedelta(hours=24)

    @property
    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()

    def __str__(self):
        return f"Reset link for {self.user.username}"
