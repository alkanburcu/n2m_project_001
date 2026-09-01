from rest_framework import serializers
from .models import Comment, Post

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id","user","title","body","created_at","updated_at",)
        read_only_fields = ("id","user","created_at", "updated_at",)

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ("id","post","user","username","body","created_at","updated_at",)

        read_only_fields = ("id","user","username","created_at", "updated_at",)