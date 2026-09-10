from authorization.permissions import HasAppPermission

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from authorization.services.resolver import has_permission

from .models import User
from .serializers import (
    ChangePasswordSerializer,
    UserCreateSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)


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

        "me": {
            "GET": "users.view",
            "PATCH": "users.update",
        },
    }

    def get_queryset(self):
        queryset = User.objects.select_related(
            "company",
            "addresses__geo",
        ).all()

        user = self.request.user

        if user.is_superuser:
            return queryset

        # Access itself is still controlled by HasAppPermission
        if self.action in (
            "list",
            "retrieve",
        ):
            return queryset

        # users.update allows updating // users.manage_others expands the target scope
        if (
            self.action
            in (
                "update",
                "partial_update",
            )
            and has_permission(
                user,
                "users.manage_others",
            )
        ):
            return queryset

        return queryset.filter(
            pk=user.pk,
        )

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer

        if self.action == "change_password":
            return ChangePasswordSerializer

        if (
            self.action == "me"
            and self.request.method == "PATCH"
        ):
            return UserProfileUpdateSerializer
        if self.action in (
            "update",
            "partial_update",
        ):
            return UserProfileUpdateSerializer

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

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
    )
    def me(self, request):
        if request.method == "GET":
            serializer = UserSerializer(
                request.user,
                context=self.get_serializer_context(),
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        response_serializer = UserSerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )