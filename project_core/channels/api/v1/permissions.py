from rest_framework import permissions
from rest_framework.permissions import BasePermission

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
        return obj.owner.user == request.user or request.user.is_supervisor 


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


class IsGetOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True


class IsOwnerSubOrReadOnly(permissions.BasePermission):
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
        # print("obj.user.user ==> ", obj.user.user)
        # print("request.user ==> ", request.user)
        # print('view => ', view)
        return obj.user.user == request.user


class IsOwnerCommentOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object or superusers.
        return (obj.user == request.user.profile) or \
                (obj.video_post.channel.owner.user.profile == request.user.profile) #or \
                #(request.user.profile in obj.video_post.channel.admins.all())


class IsOwnerCreatorOrSupervisor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user.profile or request.user.is_supervisor


class IsSupervisorOrReadonly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_supervisor


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


class IsChannelOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.channel.owner == request.user.profile