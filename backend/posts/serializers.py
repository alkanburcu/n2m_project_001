from rest_framework import serializers
from .models import Comment, Post


class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    display_name = serializers.CharField(
        source="user.display_name",
        read_only=True,
    )

    profile_photo = serializers.ImageField(
        source="user.profile_photo",
        read_only=True,
    )

    def get_display_name(self, obj):
        return obj.user.name or obj.user.username

    class Meta:
        model = Post

        fields = (
            "id",
            "user",
            "username",
            "display_name",
            "profile_photo",
            "title",
            "body",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "username",
            "display_name",
            "profile_photo",
            "created_at",
            "updated_at",
        )

        extra_kwargs = {
            "user": {
                "required": False,
            },
        }

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
                            "Post ownership cannot be changed."
                        )
                    }
                )

        return attrs

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    display_name = serializers.CharField(
        source="user.display_name",
        read_only=True,
    )

    profile_photo = serializers.ImageField(
        source="user.profile_photo",
        read_only=True,
    )

    class Meta:
        model = Comment

        fields = ("id",
                  "post",
                  "user",
                  "username",
                  "display_name",
                  "profile_photo",
                  "body",
                  "created_at",
                  "updated_at",)

        read_only_fields = ("id",
                            "user",
                            "username",
                            "display_name", 
                            "profile_photo", 
                            "created_at",
                            "updated_at",)