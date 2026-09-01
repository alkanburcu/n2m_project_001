from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


User = get_user_model()


class CurrentUserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user01",
            email="user01@test.com",
            password="Test123!",
        )

        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="Admin123!",
        )

    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED,)

    def test_normal_user_can_get_own_identity(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code,status.HTTP_200_OK,)

        self.assertEqual(str(response.data["id"]),str(self.user.id),)

        self.assertEqual(response.data["username"],self.user.username,)

        self.assertFalse(response.data["is_superuser"])

    def test_superuser_identity_contains_superuser_flag(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code,status.HTTP_200_OK,)

        self.assertEqual(str(response.data["id"]),str(self.superuser.id),)

        self.assertTrue(response.data["is_superuser"])