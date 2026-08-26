from django.urls import path

from .view import LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
]