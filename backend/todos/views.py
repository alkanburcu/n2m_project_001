from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from authorization.permissions import HasAppPermission
from authorization.services.resolver import has_permission

from .models import Todo
from .serializers import TodoSerializer


class TodoViewSet(ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [HasAppPermission]

    permission_map = {
        "list": "todos.list",
        "retrieve": "todos.view",
        "create": "todos.create",
        "update": "todos.update",
        "partial_update": "todos.update",
        "destroy": "todos.delete",
    }

    manage_others_permission = "todos.manage_others"

    def can_manage_others(self):
        return has_permission(
            self.request.user,
            self.manage_others_permission,
        )

    def get_queryset(self):
        user = self.request.user

        queryset = Todo.objects.select_related(
            "user",
        ).all()

        if not self.can_manage_others():
            queryset = queryset.filter(
                user=user,
            )

        user_id = self.request.query_params.get(
            "user",
        )

        if user_id:
            queryset = queryset.filter(
                user_id=user_id,
            )

        return queryset

    def perform_create(self, serializer):
        requesting_user = self.request.user

        target_user = serializer.validated_data.get(
            "user",
            requesting_user,
        )

        if (
            target_user != requesting_user
            and not self.can_manage_others()
        ):
            raise PermissionDenied(
                "You do not have permission to create "
                "todos for another user."
            )

        serializer.save(
            user=target_user,
        )