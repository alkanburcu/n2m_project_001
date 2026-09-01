from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsOwnerOrSuperUser

from .models import Todo
from .serializers import TodoSerializer


class TodoViewSet(ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrSuperUser,]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Todo.objects.all()

        return Todo.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)