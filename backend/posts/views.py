from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from authorization.permissions import HasAppPermission
from authorization.services.resolver import has_permission

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

    manage_others_permission = "posts.manage_others"

    def can_manage_others(self):
        return has_permission(
            self.request.user,
            self.manage_others_permission,
        )

    def get_queryset(self):
        queryset = Post.objects.select_related(
            "user",
        ).all()

        # List/retrieve davranışını şimdilik mevcut
        # sistemdeki gibi koruyoruz.
        if (
            self.action not in {"list", "retrieve"}
            and not self.can_manage_others()
        ):
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
                "posts for another user."
            )

        serializer.save(
            user=target_user,
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