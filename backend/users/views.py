from authorization.permissions import HasAppPermission
from rest_framework.viewsets import ModelViewSet

from .models import User
from .serializers import UserCreateSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    permission_classes = [HasAppPermission]

    permission_map = {
        "list": "users.list",
        "retrieve": "users.view",
        "create": "users.create",
        "update": "users.update",
        "partial_update": "users.update",
        "destroy": "users.delete",
    }

    def get_queryset(self):
        queryset = User.objects.select_related(
            "addresses__geo",
            "company",
        ).all()

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            pk=self.request.user.pk,
        )

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer

        return UserSerializer