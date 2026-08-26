from django.db import models
from backend.core.core_models import BaseModel 

class Photo(BaseModel):
    albumId = models.IntegerField()
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    url = models.URLField()
    thumbnailUrl = models.URLField()

    def __str__(self):
        return self.title
