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

        if user.is_superuser:
            return Todo.objects.all()

        return Todo.objects.filter(
            user=user,
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )