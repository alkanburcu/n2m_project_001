from rest_framework import serializers

from .models import Album, Photo


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album

        fields = ("id","user","title","created_at","updated_at",)

        read_only_fields = ("id","user","created_at","updated_at",)


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo

        fields = ("id","album","title","url","thumbnail_url","created_at","updated_at", )

        read_only_fields = ("id", "created_at","updated_at",)