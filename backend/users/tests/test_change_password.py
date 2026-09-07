from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from authorization.services.assignments import assign_default_role


User = get_user_model()


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.current_password = "Test123!"
        self.new_password = "NewSecure456!"

        self.user = User.objects.create_user(
            username="user01",
            email="user01@test.com",
            password=self.current_password,
        )

        assign_default_role(
            user=self.user,
        )

        self.url = reverse(
            "user-change-password"
        )

    def test_unauthenticated_user_cannot_change_password(
        self,
    ):
        response = self.client.post(
            self.url,
            {
                "current_password":
                    self.current_password,
                "new_password":
                    self.new_password,
                "new_password_confirm":
                    self.new_password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_wrong_current_password_is_rejected(
        self,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {
                "current_password":
                    "WrongPassword123!",
                "new_password":
                    self.new_password,
                "new_password_confirm":
                    self.new_password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "current_password",
            response.data,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.current_password
            )
        )

    def test_password_confirmation_must_match(
        self,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {
                "current_password":
                    self.current_password,
                "new_password":
                    self.new_password,
                "new_password_confirm":
                    "DifferentPassword789!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_password_confirm",
            response.data,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.current_password
            )
        )

    def test_new_password_cannot_equal_current_password(
        self,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {
                "current_password":
                    self.current_password,
                "new_password":
                    self.current_password,
                "new_password_confirm":
                    self.current_password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_password",
            response.data,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.current_password
            )
        )

    def test_weak_new_password_is_rejected(
        self,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {
                "current_password":
                    self.current_password,
                "new_password":
                    "123",
                "new_password_confirm":
                    "123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_password",
            response.data,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.current_password
            )
        )

    def test_authenticated_user_can_change_password(
        self,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {
                "current_password":
                    self.current_password,
                "new_password":
                    self.new_password,
                "new_password_confirm":
                    self.new_password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.check_password(
                self.current_password
            )
        )

        self.assertTrue(
            self.user.check_password(
                self.new_password
            )
        )