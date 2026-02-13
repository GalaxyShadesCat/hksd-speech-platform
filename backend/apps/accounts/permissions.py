from rest_framework.permissions import BasePermission

from .models import UserRole


class IsStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role in {UserRole.STAFF, UserRole.ADMIN})
