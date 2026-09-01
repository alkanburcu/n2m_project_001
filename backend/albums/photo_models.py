from django.db import models
from .models import Album
from backend.core.core_models import BaseModel 

class Photo(BaseModel):

    title = models.CharField(max_length=200)
    url = models.URLField()
    thumbnailUrl = models.URLField()

    def __str__(self):
        return self.title
