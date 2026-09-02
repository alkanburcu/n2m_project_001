from rest_framework.permissions import BasePermission

from authorization.services.resolver import has_permission


class HasAppPermission(BasePermission):
    message = "You do not have permission to perform this action."

    def get_required_permission(self, view):
        permission_map = getattr(
            view,
            "permission_map",
            {},
        )

        return permission_map.get(view.action)

    def has_permission(self, request, view):
        permission_key = self.get_required_permission(view)

        if permission_key is None:
            return False

        return has_permission(request.user,permission_key,)

    def has_object_permission(self, request, view, obj):
        permission_key = self.get_required_permission(view)

        if permission_key is None:
            return False

        return has_permission(request.user, permission_key,obj=obj,)