from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from authentication.services import (
    get_password_reset_cache_key,
)


User = get_user_model()


@override_settings(
    EMAIL_BACKEND=(
        "django.core.mail.backends."
        "locmem.EmailBackend"
    ),
    CACHES={
        "default": {
            "BACKEND": (
                "django.core.cache.backends."
                "locmem.LocMemCache"
            ),
        },
    },
)
class PasswordResetTests(APITestCase):

    def setUp(self):
        cache.clear()
        mail.outbox.clear()

        self.user = User.objects.create_user(
            username="reset_user",
            email="reset_user@test.com",
            password="OldStrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="other_user",
            email="other_user@test.com",
            password="OtherStrongPassword123!",
        )

        self.request_url = reverse(
            "password-reset-request",
        )

        self.confirm_url = reverse(
            "password-reset-confirm",
        )

    def tearDown(self):
        cache.clear()

    def request_reset_code(
        self,
        code=123456,
        username=None,
        email=None,
    ):
        with patch(
            "authentication.services."
            "secrets.randbelow",
            return_value=code,
        ):
            return self.client.post(
                self.request_url,
                {
                    "username": (
                        username
                        or self.user.username
                    ),
                    "email": (
                        email
                        or self.user.email
                    ),
                },
                format="json",
            )

    def test_password_reset_request_success(
        self,
    ):
        response = (
            self.request_reset_code()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertIn(
            "123456",
            mail.outbox[0].body,
        )

        self.assertEqual(
            mail.outbox[0].to,
            [self.user.email],
        )

    def test_valid_code_changes_password(
        self,
    ):
        self.request_reset_code()

        response = self.client.post(
            self.confirm_url,
            {
                "username":
                    self.user.username,
                "email":
                    self.user.email,
                "code": "123456",
                "new_password":
                    "NewStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewStrongPassword123!",
            )
        )

        self.assertFalse(
            self.user.check_password(
                "OldStrongPassword123!",
            )
        )

    def test_invalid_code_is_rejected(
        self,
    ):
        self.request_reset_code()

        response = self.client.post(
            self.confirm_url,
            {
                "username":
                    self.user.username,
                "email":
                    self.user.email,
                "code": "999999",
                "new_password":
                    "NewStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "OldStrongPassword123!",
            )
        )

    def test_code_can_only_be_used_once(
        self,
    ):
        self.request_reset_code()

        payload = {
            "username":
                self.user.username,
            "email":
                self.user.email,
            "code": "123456",
            "new_password":
                "NewStrongPassword123!",
        }

        first_response = (
            self.client.post(
                self.confirm_url,
                payload,
                format="json",
            )
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        payload["new_password"] = (
            "AnotherStrongPassword123!"
        )

        second_response = (
            self.client.post(
                self.confirm_url,
                payload,
                format="json",
            )
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_weak_new_password_is_rejected(
        self,
    ):
        self.request_reset_code()

        response = self.client.post(
            self.confirm_url,
            {
                "username":
                    self.user.username,
                "email":
                    self.user.email,
                "code": "123456",
                "new_password": "123",
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
                "OldStrongPassword123!",
            )
        )

    def test_invalid_code_format_is_rejected(
        self,
    ):
        self.request_reset_code()

        response = self.client.post(
            self.confirm_url,
            {
                "username":
                    self.user.username,
                "email":
                    self.user.email,
                "code": "12345",
                "new_password":
                    "NewStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "code",
            response.data,
        )

    def test_maximum_attempts_invalidates_code(
        self,
    ):
        self.request_reset_code()

        for _ in range(5):
            self.client.post(
                self.confirm_url,
                {
                    "username":
                        self.user.username,
                    "email":
                        self.user.email,
                    "code": "999999",
                    "new_password":
                        "NewStrongPassword123!",
                },
                format="json",
            )

        response = self.client.post(
            self.confirm_url,
            {
                "username":
                    self.user.username,
                "email":
                    self.user.email,
                "code": "123456",
                "new_password":
                    "NewStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "OldStrongPassword123!",
            )
        )

    def test_resend_cooldown_does_not_send_second_email(
        self,
    ):
        first_response = (
            self.request_reset_code(
                code=123456,
            )
        )

        second_response = (
            self.request_reset_code(
                code=654321,
            )
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

    def test_expired_or_missing_code_is_rejected(
        self,
    ):
        cache_key = (
            get_password_reset_cache_key(
                self.user.id,
            )
        )

        cache.set(
            cache_key,
            {
                "user_id":
                    str(self.user.id),
                "code_hash":
                    make_password(
                        "123456",
                    ),
                "attempts": 0,
                "expires_at": 0,
            },
            timeout=0,
        )

        response = self.client.post(
            self.confirm_url,
            {
                "username":
                    self.user.username,
                "email":
                    self.user.email,
                "code": "123456",
                "new_password":
                    "NewStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unknown_account_is_rejected(
    self,
):
        response = self.client.post(
            self.request_url,
            {
                "username": "does_not_exist",
                "email": "nobody@test.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_mismatched_username_and_email_does_not_send_code(
    self,
):
        response = self.request_reset_code(
            username=self.user.username,
            email=self.other_user.email,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

        self.assertEqual(
            response.data["error"],
            "The username or email is incorrect.",
        )
    def test_code_cannot_be_used_for_another_account(
        self,
    ):
        self.request_reset_code()

        response = self.client.post(
            self.confirm_url,
            {
                "username":
                    self.other_user.username,
                "email":
                    self.other_user.email,
                "code": "123456",
                "new_password":
                    "HijackedPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.other_user.refresh_from_db()

        self.assertTrue(
            self.other_user.check_password(
                "OtherStrongPassword123!",
            )
        )