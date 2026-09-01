from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUser(BasePermission):
    message = "Only superusers can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )

class IsOwnerOrSuperUser(BasePermission):
    message = "You do not have permission to modify this object."

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        return obj.user == request.user


class IsOwnerOrSuperUserOrReadOnly(BasePermission):
    message = "You do not have permission to modify this object."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        return obj.user == request.user