from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import (
    IsAlbumOwnerOrSuperUser,
    IsOwnerOrSuperUser,
)

from .models import Album, Photo
from .serializers import AlbumSerializer, PhotoSerializer


class AlbumViewSet(ModelViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrSuperUser,]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Album.objects.select_related("user").all()

        return Album.objects.select_related("user").filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PhotoViewSet(ModelViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [
        IsAuthenticated,
        IsAlbumOwnerOrSuperUser,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            queryset = Photo.objects.select_related("album","album__user",).all()
        else:
            queryset = Photo.objects.select_related("album","album__user",).filter(album__user=user)

        album_id = self.request.query_params.get("album")

        if album_id:
            queryset = queryset.filter(album_id=album_id)

        return queryset

    def perform_create(self, serializer):
        album = serializer.validated_data["album"]

        if (
            not self.request.user.is_superuser
            and album.user != self.request.user
        ):
            raise PermissionDenied(
                "You cannot add photos to another user's album."
            )

        serializer.save()