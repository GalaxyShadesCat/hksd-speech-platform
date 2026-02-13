from django.contrib import admin

from .models import Centre


@admin.register(Centre)
class CentreAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
