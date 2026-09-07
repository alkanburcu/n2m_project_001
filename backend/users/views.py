from authorization.permissions import HasAppPermission
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from rest_framework import status
from .serializers import UserCreateSerializer, UserSerializer,ChangePasswordSerializer

class UserViewSet(ModelViewSet):
    permission_classes = [HasAppPermission]

    permission_map = {
        "list": "users.list",
        "retrieve": "users.view",
        "create": "users.create",
        "update": "users.update",
        "partial_update": "users.update",
        "destroy": "users.delete",
        "change_password": "users.update",
    }

    def get_queryset(self):
        queryset = User.objects.select_related(
            "company",
            "addresses__geo",
        ).all()

        if self.request.user.is_superuser:
            return queryset

        if self.action == "retrieve":
            return queryset

        return queryset.filter(
            pk=self.request.user.pk,
        )

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer

        if self.action == "change_password":
            return ChangePasswordSerializer

        return UserSerializer

    @action(
        detail=False,
        methods=["post"],
        url_path="change-password",
    )
    def change_password(self, request):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Password changed successfully."
                )
            },
            status=status.HTTP_200_OK,
        )