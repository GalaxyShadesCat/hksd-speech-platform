from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import UserProfile, UserRole
from .services import sync_role_group_membership

User = get_user_model()
GROUPS = ["HKSD_ADMIN", "HKSD_STAFF", "HKSD_PARENT"]


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    for name in GROUPS:
        Group.objects.get_or_create(name=name)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if not created:
        return

    profile, _ = UserProfile.objects.get_or_create(user=instance)
    if profile.role != UserRole.PARENT:
        profile.role = UserRole.PARENT
        profile.save(update_fields=["role"])


@receiver(post_save, sender=UserProfile)
def update_user_groups(sender, instance, **kwargs):
    sync_role_group_membership(instance.user)
