from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.models import UserEmail
from users.services.user_service import (
    create_application_user,
)


User = get_user_model()


class UserCreationTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="Admin123!",
        )

        self.existing_user = (
            create_application_user(
                username="existing_user",
                email="existing@test.com",
                password="Test123!",
            )
        )

        self.url = reverse("user-list")

    def test_duplicate_email_is_rejected(
        self,
    ):
        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.post(
            self.url,
            {
                "username": "new_user",
                "email": "EXISTING@test.com",
                "password": "NewStrong123!",
                "password_confirm": "NewStrong123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "email",
            response.data,
        )

        self.assertFalse(
            User.objects.filter(
                username="new_user",
            ).exists()
        )

        self.assertEqual(
            UserEmail.objects.filter(
                email__iexact="existing@test.com",
            ).count(),
            1,
        )