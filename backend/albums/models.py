from django.db import models
from django.conf import settings
from core.core_models import BaseModel 

class Album(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="albums")
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Photo(BaseModel):
    album = models.ForeignKey(Album,on_delete=models.CASCADE,related_name="photos")

    title = models.CharField(max_length=200)
    url = models.URLField()
    thumbnail_url = models.URLField()

    def __str__(self):
        return self.title
