from rest_framework import permissions


# Is Owner or Read Only Permission
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.product_user.id == request.user.id


# Is Owner Only Permission
class IsOwnerOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user.id == request.user.id