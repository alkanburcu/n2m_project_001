from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend") 


class PasswordResetTests(APITestCase):

    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            username="reset_user",
            email="reset_user@test.com",
            password="OldStrongPassword123!",
        )

        self.request_url = reverse("password-reset-request")

        self.confirm_url = reverse("password-reset-confirm")

    def tearDown(self):
        cache.clear()

    def request_reset_code(self, code=123456):
        with patch("authentication.services.secrets.randbelow",return_value=code,):
            return self.client.post(self.request_url, {"email": self.user.email,},)

    def test_password_reset_request_success(self):
        response = self.request_reset_code()

        self.assertEqual(response.status_code, status.HTTP_200_OK,)

        self.assertEqual(len(mail.outbox),1,)

        self.assertIn("123456", mail.outbox[0].body,)

    def test_valid_code_changes_password(self):
        self.request_reset_code()

        response = self.client.post(
            self.confirm_url,
            {
                "email": self.user.email,
                "code": "123456",
                "new_password": "NewStrongPassword123!",
            },
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK,)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("NewStrongPassword123!"))

        self.assertFalse(self.user.check_password("OldStrongPassword123!"))

    def test_invalid_code_is_rejected(self):
        self.request_reset_code()

        response = self.client.post(
            self.confirm_url,
            {
                "email": self.user.email,
                "code": "999999",
                "new_password": "NewStrongPassword123!",
            },
        )

        self.assertEqual( response.status_code,status.HTTP_400_BAD_REQUEST,)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("OldStrongPassword123!"))

    def test_code_can_only_be_used_once(self):
        self.request_reset_code()

        first_response = self.client.post(
            self.confirm_url,
            {
                "email": self.user.email,
                "code": "123456",
                "new_password": "NewStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(first_response.status_code,status.HTTP_200_OK,)

        second_response = self.client.post(
            self.confirm_url,
            {
                "email": self.user.email,
                "code": "123456",
                "new_password": "AnotherStrongPassword123!",
            },
        )

        self.assertEqual(second_response.status_code,status.HTTP_400_BAD_REQUEST,)

    def test_weak_new_password_is_rejected(self):
        self.request_reset_code()

        response = self.client.post(
            self.confirm_url,
            {
                "email": self.user.email,
                "code": "123456",
                "new_password": "123",
            },
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

        self.assertIn( "new_password",response.data,)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("OldStrongPassword123!"))

    def test_invalid_code_format_is_rejected(self):
        self.request_reset_code()

        response = self.client.post(
            self.confirm_url,
            {
                "email": self.user.email,
                "code": "12345",
                "new_password": "NewStrongPassword123!",
            },
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

        self.assertIn("code", response.data,)

    def test_maximum_attempts_invalidates_code(self):
        self.request_reset_code()

        for _ in range(5):
            self.client.post(
                self.confirm_url,
                {
                    "email": self.user.email,
                    "code": "999999",
                    "new_password": "NewStrongPassword123!",
                },
            )

        response = self.client.post(
            self.confirm_url,
            {
                "email": self.user.email,
                "code": "123456",
                "new_password": "NewStrongPassword123!",
            },
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("OldStrongPassword123!"))

    def test_resend_cooldown_does_not_send_second_email(self):
        first_response = self.request_reset_code(code=123456)

        second_response = self.request_reset_code(code=654321)

        self.assertEqual(first_response.status_code,status.HTTP_200_OK,)

        self.assertEqual(second_response.status_code,status.HTTP_200_OK,)

        self.assertEqual(len(mail.outbox),1,)

    def test_expired_or_missing_code_is_rejected(self):
        cache_key = (f"password_reset:{self.user.email.lower()}")

        cache.set(cache_key,{"code_hash": make_password("123456"),"attempts": 0,},timeout=0,)

        response = self.client.post(
            self.confirm_url,
            {
                "email": self.user.email,
                "code": "123456",
                "new_password": "NewStrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,)

    def test_unknown_email_request_has_generic_response(self):
        response = self.client.post(self.request_url,{"email": "nobody@test.com",},)

        self.assertEqual(response.status_code,status.HTTP_200_OK,)

        self.assertEqual(len(mail.outbox),0,)