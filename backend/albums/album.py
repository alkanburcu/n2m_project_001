from django.db import models
from backend.core.core_models import BaseModel 

class Album(BaseModel):
    userId = models.IntegerField()
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title