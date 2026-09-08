from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .views import CurrentUserView
from .views import LoginView, PasswordResetRequestView, PasswordResetConfirmView, RegisterView, PasswordResetRedeemView

router = DefaultRouter()

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("password-reset-request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset-redeem/",PasswordResetRedeemView.as_view(),name="password-reset-redeem",),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("me/", CurrentUserView.as_view(), name="me"),
]

urlpatterns += router.urls