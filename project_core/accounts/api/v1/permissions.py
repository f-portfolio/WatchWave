from django.contrib.auth.decorators import user_passes_test
from rest_framework import permissions


def verified_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def is_verified(user):
        if user.is_verified():
            return True
        return False
    return user_passes_test(is_verified)

class IsSuperUserOrSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, 'is_supervisor', False))

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsGetOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
