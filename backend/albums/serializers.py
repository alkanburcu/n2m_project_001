from rest_framework import serializers

from .models import Album, Photo

class AlbumPreviewPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo

        fields = ("id","image",)


class AlbumSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(
        read_only=True,
    )

    preview_photos = serializers.SerializerMethodField()

    class Meta:
        model = Album

        fields = (
            "id",
            "user",
            "title",
            "photo_count",
            "preview_photos",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

        extra_kwargs = {
            "user": {
                "required": False,
            },
        }

    def get_preview_photos(self, obj):
        photos = list(obj.photos.all())[:4]

        return AlbumPreviewPhotoSerializer(
            photos,
            many=True,
            context=self.context,
        ).data

    def validate(self, attrs):
        if self.instance is not None:
            requested_user = attrs.get("user")

            if (
                requested_user is not None
                and requested_user != self.instance.user
            ):
                raise serializers.ValidationError(
                    {
                        "user": (
                            "Album ownership cannot be changed."
                        )
                    }
                )

        return attrs


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo

        fields = ("id","album","title","image","created_at","updated_at", )

        read_only_fields = ("id", "created_at","updated_at",)