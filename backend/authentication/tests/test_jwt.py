from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


User = get_user_model()


class JWTTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        self.refresh_url = reverse("token-refresh")
        self.logout_url = reverse("logout")

        refresh = RefreshToken.for_user(self.user)

        self.refresh_token = str(refresh)
        self.access_token = str(refresh.access_token)

    def test_refresh_returns_new_access_and_refresh(self):
        response = self.client.post( self.refresh_url,{"refresh": self.refresh_token},)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token_is_rotated(self):
        response = self.client.post(self.refresh_url, {"refresh": self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_refresh = response.data["refresh"]

        self.assertNotEqual(self.refresh_token, new_refresh)

    def test_old_refresh_is_blacklisted_after_rotation(self):
        first_response = self.client.post(self.refresh_url, {"refresh": self.refresh_token})

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        second_response = self.client.post(self.refresh_url, {"refresh": self.refresh_token})

        self.assertEqual(second_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_new_refresh_can_be_used_after_rotation(self):
        first_response = self.client.post(self.refresh_url, {"refresh": self.refresh_token})

        new_refresh = first_response.data["refresh"]

        second_response = self.client.post(self.refresh_url, {"refresh": new_refresh})

        self.assertEqual(second_response.status_code,status.HTTP_200_OK)
        self.assertIn("access", second_response.data)
        self.assertIn("refresh", second_response.data)

    def test_logout_blacklists_refresh_token(self):
        logout_response = self.client.post(self.logout_url, {"refresh": self.refresh_token})

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(self.refresh_url,{"refresh": self.refresh_token})

        self.assertEqual(refresh_response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_invalid_refresh_token_is_rejected(self):
        response = self.client.post(self.refresh_url,{"refresh": "invalid-token"})

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_access_token_lifetime_is_15_minutes(self):
        access = AccessToken(self.access_token)

        lifetime = access["exp"] - access["iat"]

        self.assertEqual(lifetime, 15 * 60)

    def test_refresh_token_lifetime_is_1_day(self):
        refresh = RefreshToken(self.refresh_token)

        lifetime = refresh["exp"] - refresh["iat"]

        self.assertEqual(lifetime, 24 * 60 * 60)