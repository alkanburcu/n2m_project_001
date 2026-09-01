from core.permissions import IsSuperUser
from rest_framework.viewsets import ModelViewSet

from .models import User
from .serializers import UserCreateSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.select_related(
        "addresses__geo",
        "company",
    ).all()


    permission_classes = [IsSuperUser]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer

        return UserSerializer