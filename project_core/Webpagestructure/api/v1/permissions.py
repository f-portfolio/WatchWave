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


class IsSuperVisorUser(permissions.BasePermission):
    """
    Allows access only to supervisor users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_supervisor


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return request.user.is_supervisor


from rest_framework.permissions import BasePermission

class IsSuperuser(BasePermission):
    """
    Only allows access to superusers.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


from rest_framework.permissions import BasePermission

class IsSupervisor(BasePermission):
    """
    Allows access only to users with 'is_supervisor' attribute set to True.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'is_supervisor', False)



class IsOwnerOrSupervisor(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or superusers to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object or superusers.
        return obj.publisher == request.user.profile or request.user.is_supervisor or obj.channel.owner == request.user.profile


class ProposerOrSupervisor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.proposing_user == request.user.profile or request.user.is_supervisor


class IsOwnerOrSupervisor_Item(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user.profile or request.user.is_supervisor

