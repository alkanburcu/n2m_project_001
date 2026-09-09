from django.db import models
from django.conf import settings
from django.db.models import Q
from django.db.models.functions import Lower

from companies.models import Company
from django.contrib.auth.models import AbstractUser
from core.core_models import BaseModel

class User(AbstractUser, BaseModel):
    name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    website = models.URLField(max_length=200, blank=True)
    location = models.CharField( max_length=150,blank=True,)

    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        null=True,
        blank=True,
    )

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def __str__(self):
        return self.username

class Adress(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=100)
    suite = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.zipcode}"

class geo(BaseModel):
    address = models.OneToOneField(Adress, on_delete=models.CASCADE, related_name='geo')
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return f"Lat: {self.lat}, Lng: {self.lng}"

class UserEmail(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emails",
    )

    email = models.EmailField()

    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="unique_user_email_ci",
            ),
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_primary=True),
                name="unique_primary_email_per_user",
            ),
        ]

    def __str__(self):
        return self.email