from django.db import models
from backend.core.core_models import BaseModel

class Post(BaseModel):
    userId = models.IntegerField()
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return self.title
    