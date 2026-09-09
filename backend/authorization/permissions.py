from rest_framework.permissions import BasePermission

from authorization.services.resolver import has_permission


class HasAppPermission(BasePermission):
    message = "You do not have permission to perform this action."

    def get_required_permission(
        self,
        view,
        request=None,
    ):
        permission_map = getattr(
            view,
            "permission_map",
            {},
        )

        required_permission = permission_map.get(
            view.action
        )

        if isinstance(
            required_permission,
            dict,
        ):
            if request is None:
                return None

            return required_permission.get(
                request.method
            )

        return required_permission

    def has_permission(
        self,
        request,
        view,
    ):
        permission_key = (
            self.get_required_permission(
                view,
                request,
            )
        )

        if permission_key is None:
            return False

        return has_permission(
            request.user,
            permission_key,
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        permission_key = (
            self.get_required_permission(
                view,
                request,
            )
        )

        if permission_key is None:
            return False

        return has_permission(
            request.user,
            permission_key,
            obj=obj,
        )