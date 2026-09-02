from rest_framework.viewsets import ModelViewSet

from authorization.permissions import HasAppPermission

from .models import Comment, Post
from .serializers import CommentSerializer, PostSerializer


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [HasAppPermission]

    permission_map = {
        "list": "posts.list",
        "retrieve": "posts.view",
        "create": "posts.create",
        "update": "posts.update",
        "partial_update": "posts.update",
        "destroy": "posts.delete",
    }

    def get_queryset(self):
        queryset = Post.objects.select_related(
            "user"
        ).all()

        if (
            self.request.user.is_superuser
            or self.action in {"list", "retrieve"}
        ):
            return queryset

        return queryset.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [HasAppPermission]

    permission_map = {
        "list": "comments.list",
        "retrieve": "comments.view",
        "create": "comments.create",
        "update": "comments.update",
        "partial_update": "comments.update",
        "destroy": "comments.delete",
    }

    def get_queryset(self):
        queryset = Comment.objects.select_related(
            "user",
            "post",
        ).all()

        if (
            not self.request.user.is_superuser
            and self.action not in {"list", "retrieve"}
        ):
            queryset = queryset.filter(
                user=self.request.user
            )

        post_id = self.request.query_params.get(
            "post"
        )

        if post_id:
            queryset = queryset.filter(
                post_id=post_id
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )