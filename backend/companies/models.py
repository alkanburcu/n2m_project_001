from django.db import models

# Create your models here.
from django.db import models

from core.core_models import BaseModel


class Company(BaseModel):
    name = models.CharField(
        max_length=150,
        db_index=True,
    )

    address = models.CharField(
        max_length=255,
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    phone_number = models.CharField(
        max_length=30,
        blank=True,
    )

    website = models.URLField(
        max_length=200,
        blank=True,
    )

    def __str__(self):
        return self.name