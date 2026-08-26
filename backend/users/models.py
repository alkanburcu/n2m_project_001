from django.db import models
from django.contrib.auth.models import AbstractUser
from core.core_models import BaseModel

class User(AbstractUser, BaseModel):
    name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    website = models.URLField(max_length=200, blank=True)

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

class Company(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

