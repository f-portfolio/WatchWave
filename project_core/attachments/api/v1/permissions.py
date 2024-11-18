from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class IsGetOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True


from rest_framework.permissions import BasePermission



class IsSupervisor(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    #def has_permission(self, request, view):
    #    return bool(request.user and request.user.is_supervisor)
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_supervisor 


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
        return obj.supervisor_to_add == request.user.profile or request.user.is_supervisor


class IsOwnerOrSupervisor_Item(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or superusers to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object or superusers.
        return obj.user == request.user.profile or request.user.is_supervisor


class ProposerOrSupervisor(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or superusers to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object or superusers.
        return obj.proposing_user == request.user.profile or request.user.is_supervisor


class OwnerAddOrSupV(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or superusers to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object or superusers.
        return obj.user_adder == request.user.profile or request.user.is_supervisor

