from rest_framework import permissions


# Is Owner or Read Only Permission
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.product_user.id == request.user.id


# Is StoreOwner Or Read Only Permission
class IsStoreOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and obj.store_user.id == request.user.id


# Only Verified User Permission
class IsOnlyVerifiedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.verified:
            return True
        return False


# Is Owner Only Permission
class IsOwnerOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user.id == request.user.id