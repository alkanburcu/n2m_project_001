from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsOwnerOrSuperUserOrReadOnly

from .models import Post
from .serializers import PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related("user").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrSuperUserOrReadOnly,]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)