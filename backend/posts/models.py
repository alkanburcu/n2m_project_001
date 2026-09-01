from django.db import models
from django.conf import settings
from core.core_models import BaseModel

class Post(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="posts")

    title = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return self.title
    
class Comment(BaseModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField()

    def __str__(self):
        return f"Comment by {self.user.username}"

