from django.contrib import admin

from .models import PasswordResetLink, UserProfile, UserRole


def _is_full_admin(request):
    if request.user.is_superuser:
        return True
    profile = getattr(request.user, "profile", None)
    return bool(profile and profile.role == UserRole.ADMIN)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "centre", "created_at")
    list_filter = ("role", "centre")
    search_fields = ("user__username",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("user", "centre")
        if _is_full_admin(request):
            return queryset

        staff_profile = getattr(request.user, "profile", None)
        if not staff_profile or staff_profile.role != UserRole.STAFF:
            return queryset.none()

        return queryset.filter(role=UserRole.PARENT, centre_id=staff_profile.centre_id)


@admin.register(PasswordResetLink)
class PasswordResetLinkAdmin(admin.ModelAdmin):
    list_display = ("user", "created_by", "created_at", "expires_at", "used_at")
    list_filter = ("created_at", "expires_at")
    search_fields = ("user__username", "created_by__username")
    readonly_fields = ("token", "uidb64", "created_at")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("user", "created_by")
        if _is_full_admin(request):
            return queryset

        staff_profile = getattr(request.user, "profile", None)
        if not staff_profile or staff_profile.role != UserRole.STAFF:
            return queryset.none()

        return queryset.filter(user__profile__centre_id=staff_profile.centre_id)
