from django.contrib import admin

from apps.accounts.models import UserRole

from .models import AgeBand, ScreeningAttempt, ScreeningItem, ScreeningSession, ScreeningSet


def _is_full_admin(request):
    if request.user.is_superuser:
        return True
    profile = getattr(request.user, "profile", None)
    return bool(profile and profile.role == UserRole.ADMIN)


class ScreeningItemInline(admin.TabularInline):
    model = ScreeningItem
    extra = 1


@admin.register(AgeBand)
class AgeBandAdmin(admin.ModelAdmin):
    list_display = ("label", "min_months", "max_months", "is_active")
    list_filter = ("is_active",)
    search_fields = ("label",)


@admin.register(ScreeningSet)
class ScreeningSetAdmin(admin.ModelAdmin):
    list_display = ("name", "age_band", "centre", "is_active")
    list_filter = ("age_band", "centre", "is_active")
    search_fields = ("name",)
    inlines = [ScreeningItemInline]


@admin.register(ScreeningSession)
class ScreeningSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "centre", "age_band", "started_at", "submitted_at")
    list_filter = ("centre", "age_band", "started_at")
    search_fields = ("created_by__username",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("created_by", "centre", "age_band")
        if _is_full_admin(request):
            return queryset
        profile = getattr(request.user, "profile", None)
        if not profile or profile.role != UserRole.STAFF:
            return queryset.none()
        return queryset.filter(centre_id=profile.centre_id)


@admin.register(ScreeningAttempt)
class ScreeningAttemptAdmin(admin.ModelAdmin):
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
