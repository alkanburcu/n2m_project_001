from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from authorization.permissions import HasAppPermission
from authorization.services.resolver import has_permission

from .models import Album, Photo
from .serializers import AlbumSerializer, PhotoSerializer
from django.db.models import Count


class AlbumViewSet(ModelViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [HasAppPermission]

    permission_map = {
        "list": "albums.list",
        "retrieve": "albums.view",
        "create": "albums.create",
        "update": "albums.update",
        "partial_update": "albums.update",
        "destroy": "albums.delete",
    }

    manage_others_permission = "albums.manage_others"

    def can_manage_others(self):
        return has_permission(
            self.request.user,
            self.manage_others_permission,
        )

    def get_queryset(self):
        queryset = (
            Album.objects
            .select_related("user")
            .prefetch_related("photos")
            .annotate(
                photo_count=Count("photos"),
            )
        )
        if not self.can_manage_others():
            queryset = queryset.filter(
                user=self.request.user,
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
                "albums for another user."
            )

        serializer.save(
            user=target_user,
        )


class PhotoViewSet(ModelViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [HasAppPermission]

    permission_map = {
        "list": "photos.list",
        "retrieve": "photos.view",
        "create": "photos.create",
        "update": "photos.update",
        "partial_update": "photos.update",
        "destroy": "photos.delete",
    }

    manage_others_permission = "photos.manage_others"

    def can_manage_others(self):
        return has_permission(
            self.request.user,
            self.manage_others_permission,
        )

    def get_queryset(self):
        queryset = Photo.objects.select_related(
            "album",
            "album__user",
        ).all()

        if not self.can_manage_others():
            queryset = queryset.filter(
                album__user=self.request.user,
            )

        album_id = self.request.query_params.get(
            "album",
        )

        if album_id:
            queryset = queryset.filter(
                album_id=album_id,
            )

        return queryset

    def _check_album_scope(self, serializer):
        album = serializer.validated_data.get(
            "album",
        )

        if album is None:
            return

        if (
            album.user_id != self.request.user.id
            and not self.can_manage_others()
        ):
            raise PermissionDenied(
                "You do not have permission to manage "
                "photos in another user's album."
            )

    def perform_create(self, serializer):
        self._check_album_scope(serializer)
        serializer.save()

    def perform_update(self, serializer):
        self._check_album_scope(serializer)
        serializer.save()