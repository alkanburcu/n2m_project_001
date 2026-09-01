from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Comment, Post
from .serializers import CommentSerializer, PostSerializer

from core.permissions import IsOwnerOrSuperUserOrReadOnly


class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related("user").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrSuperUserOrReadOnly,]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.select_related("user","post",).all()

    serializer_class = CommentSerializer

    permission_classes = [
        IsAuthenticated,
        IsOwnerOrSuperUserOrReadOnly,
    ]

    def get_queryset(self):
        queryset = self.queryset

        post_id = self.request.query_params.get("post")

        if post_id:
            queryset = queryset.filter(post_id=post_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)