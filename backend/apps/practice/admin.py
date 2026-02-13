from django.contrib import admin

from apps.accounts.models import UserRole

from .models import PracticeAttempt, PracticeItem, PracticeSession


def _is_full_admin(request):
    if request.user.is_superuser:
        return True
    profile = getattr(request.user, "profile", None)
    return bool(profile and profile.role == UserRole.ADMIN)


class PracticeItemInline(admin.TabularInline):
    model = PracticeItem
    extra = 0


class PracticeAttemptInline(admin.TabularInline):
    model = PracticeAttempt
    extra = 0


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "centre", "session_type", "started_at", "submitted_at")
    list_filter = ("session_type", "centre", "started_at")
    search_fields = ("created_by__username", "child_display_name")
    inlines = [PracticeItemInline, PracticeAttemptInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("created_by", "centre")
        if _is_full_admin(request):
            return queryset
        profile = getattr(request.user, "profile", None)
        if not profile or profile.role != UserRole.STAFF:
            return queryset.none()
        return queryset.filter(centre_id=profile.centre_id)


@admin.register(PracticeItem)
class PracticeItemAdmin(admin.ModelAdmin):
    list_display = ("session", "position", "word")
    list_filter = ("session__centre",)
    search_fields = ("session__created_by__username", "word__hanzi", "word__jyutping")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("session", "word")
        if _is_full_admin(request):
            return queryset
        profile = getattr(request.user, "profile", None)
        if not profile or profile.role != UserRole.STAFF:
            return queryset.none()
        return queryset.filter(session__centre_id=profile.centre_id)


@admin.register(PracticeAttempt)
class PracticeAttemptAdmin(admin.ModelAdmin):
    list_display = ("session", "position", "word", "is_correct")
    list_filter = ("is_correct", "session__centre")
    search_fields = ("session__created_by__username", "word__hanzi", "word__jyutping")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("session", "word")
        if _is_full_admin(request):
            return queryset
        profile = getattr(request.user, "profile", None)
        if not profile or profile.role != UserRole.STAFF:
            return queryset.none()
        return queryset.filter(session__centre_id=profile.centre_id)
