from rest_framework.viewsets import ModelViewSet

from authorization.permissions import HasAppPermission

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

    def get_queryset(self):
        user = self.request.user

        queryset = Todo.objects.all()

        if not user.is_superuser:
            queryset = queryset.filter(
                user=user,
            )

        user_id = self.request.query_params.get(
            "user"
        )

        if user_id:
            queryset = queryset.filter(
                user_id=user_id,
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )