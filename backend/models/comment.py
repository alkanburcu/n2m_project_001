from django.db import models
from backend.core.core_models import BaseModel 

class Comment(BaseModel):
    postId = models.IntegerField()
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    body = models.TextField()

    def __str__(self):
        return self.name
    