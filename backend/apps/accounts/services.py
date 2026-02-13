from django.contrib.auth.models import Group

from .models import UserRole


def sync_role_group_membership(user):
    profile = getattr(user, "profile", None)
    if not profile:
        return

    mapping = {
        UserRole.ADMIN: "HKSD_ADMIN",
        UserRole.STAFF: "HKSD_STAFF",
        UserRole.PARENT: "HKSD_PARENT",
    }
    target_name = mapping.get(profile.role)
    if not target_name:
        return

    target_group, _ = Group.objects.get_or_create(name=target_name)
    for group_name in mapping.values():
        group, _ = Group.objects.get_or_create(name=group_name)
        if group.id != target_group.id:
            user.groups.remove(group)
    user.groups.add(target_group)

    # Keep Django admin flags aligned with HKSD roles.
    if profile.role == UserRole.ADMIN:
        desired_is_staff = True
        desired_is_superuser = True
    elif profile.role == UserRole.STAFF:
        desired_is_staff = True
        desired_is_superuser = False
    else:
        desired_is_staff = False
        desired_is_superuser = False

    changed_fields = []
    if user.is_staff != desired_is_staff:
        user.is_staff = desired_is_staff
        changed_fields.append("is_staff")
    if user.is_superuser != desired_is_superuser:
        user.is_superuser = desired_is_superuser
        changed_fields.append("is_superuser")

    if changed_fields:
        user.save(update_fields=changed_fields)
