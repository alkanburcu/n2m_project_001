import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserEmail


User = get_user_model()


@override_settings(
    EMAIL_BACKEND=(
        "django.core.mail.backends."
        "locmem.EmailBackend"
    ),
    FRONTEND_BASE_URL="http://localhost:5173",
)
class PasswordResetTests(APITestCase):

    def setUp(self):
        mail.outbox.clear()

        self.old_password = (
            "OldStrongPassword123!"
        )

        self.new_password = (
            "NewStrongPassword456!"
        )

        self.user = User.objects.create_user(
            username="reset_user",
            email="reset_user@test.com",
            password=self.old_password,
        )

        self.user_email = (
            UserEmail.objects.create(
                user=self.user,
                email="reset_user@test.com",
                is_primary=True,
                is_active=True,
            )
        )

        self.other_user = (
            User.objects.create_user(
                username="other_user",
                email="other_user@test.com",
                password=(
                    "OtherStrongPassword123!"
                ),
            )
        )

        self.other_user_email = (
            UserEmail.objects.create(
                user=self.other_user,
                email="other_user@test.com",
                is_primary=True,
                is_active=True,
            )
        )

        self.request_url = reverse(
            "password-reset-request",
        )

        self.confirm_url = reverse(
            "password-reset-confirm",
        )

    def request_reset_link(
        self,
        email=None,
    ):
        return self.client.post(
            self.request_url,
            {
                "email": (
                    email
                    or self.user_email.email
                ),
            },
            format="json",
        )

    def get_reset_credentials(self):
        self.assertEqual(
            len(mail.outbox),
            1,
        )

        body = mail.outbox[0].body

        match = re.search(
            (
                r"/reset-password/"
                r"([^/\s]+)/([^/\s]+)"
            ),
            body,
        )

        self.assertIsNotNone(
            match,
        )

        uid = match.group(1)
        token = match.group(2)

        return uid, token

    def test_password_reset_request_success(
        self,
    ):
        response = (
            self.request_reset_link()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertEqual(
            mail.outbox[0].to,
            [self.user_email.email],
        )

        self.assertIn(
            "/reset-password/",
            mail.outbox[0].body,
        )

    def test_unknown_email_returns_generic_success(
        self,
    ):
        response = (
            self.request_reset_link(
                email=(
                    "unknown@test.com"
                ),
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_invalid_email_format_is_rejected(
        self,
    ):
        response = (
            self.request_reset_link(
                email="invalid-email",
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "email",
            response.data,
        )

    def test_inactive_user_does_not_receive_email(
        self,
    ):
        self.user.is_active = False

        self.user.save(
            update_fields=["is_active"],
        )

        response = (
            self.request_reset_link()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_inactive_email_does_not_receive_email(
        self,
    ):
        self.user_email.is_active = False

        self.user_email.save(
            update_fields=["is_active"],
        )

        response = (
            self.request_reset_link()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_email_lookup_is_case_insensitive(
        self,
    ):
        response = (
            self.request_reset_link(
                email=(
                    "RESET_USER@TEST.COM"
                ),
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

    def test_valid_link_changes_password(
        self,
    ):
        self.request_reset_link()

        uid, token = (
            self.get_reset_credentials()
        )

        response = self.client.post(
            self.confirm_url,
            {
                "uid": uid,
                "token": token,
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
                self.old_password,
            )
        )

        self.assertTrue(
            self.user.check_password(
                self.new_password,
            )
        )

    def test_invalid_token_is_rejected(
        self,
    ):
        self.request_reset_link()

        uid, _ = (
            self.get_reset_credentials()
        )

        response = self.client.post(
            self.confirm_url,
            {
                "uid": uid,
                "token": "invalid-token",
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

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.old_password,
            )
        )

    def test_reset_link_cannot_be_reused(
        self,
    ):
        self.request_reset_link()

        uid, token = (
            self.get_reset_credentials()
        )

        first_response = self.client.post(
            self.confirm_url,
            {
                "uid": uid,
                "token": token,
                "new_password":
                    self.new_password,
                "new_password_confirm":
                    self.new_password,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        second_response = (
            self.client.post(
                self.confirm_url,
                {
                    "uid": uid,
                    "token": token,
                    "new_password": (
                        "AnotherStrongPassword789!"
                    ),
                    "new_password_confirm": (
                        "AnotherStrongPassword789!"
                    ),
                },
                format="json",
            )
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_current_password_cannot_be_reused(
        self,
    ):
        self.request_reset_link()

        uid, token = (
            self.get_reset_credentials()
        )

        response = self.client.post(
            self.confirm_url,
            {
                "uid": uid,
                "token": token,
                "new_password":
                    self.old_password,
                "new_password_confirm":
                    self.old_password,
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
                self.old_password,
            )
        )

    def test_password_confirmation_must_match(
        self,
    ):
        self.request_reset_link()

        uid, token = (
            self.get_reset_credentials()
        )

        response = self.client.post(
            self.confirm_url,
            {
                "uid": uid,
                "token": token,
                "new_password":
                    self.new_password,
                "new_password_confirm": (
                    "DifferentPassword789!"
                ),
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
                self.old_password,
            )
        )

    def test_weak_new_password_is_rejected(
        self,
    ):
        self.request_reset_link()

        uid, token = (
            self.get_reset_credentials()
        )

        response = self.client.post(
            self.confirm_url,
            {
                "uid": uid,
                "token": token,
                "new_password": "123",
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
                self.old_password,
            )
        )
    def test_password_reset_uses_user_email_not_legacy_user_email(
        self,
    ):
        self.user.email = "legacy@test.com"
        self.user.save(
            update_fields=["email"],
        )

        response = self.request_reset_link(
            email=self.user_email.email,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertEqual(
            mail.outbox[0].to,
            [self.user_email.email],
        )

    def test_legacy_user_email_cannot_trigger_password_reset(
        self,
    ):
        self.user.email = "legacy@test.com"
        self.user.save(
            update_fields=["email"],
        )

        response = self.request_reset_link(
            email="legacy@test.com",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )
    def test_password_reset_email_contains_html_button(
    self,
    ):
        response = self.request_reset_link()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        email_message = mail.outbox[0]

        self.assertEqual(
            len(email_message.alternatives),
            1,
        )

        html_content = (
            email_message.alternatives[0].content
        )

        self.assertIn(
            "Reset Password",
            html_content,
        )

        self.assertIn(
            "http://localhost:5173/reset-password/",
            html_content,
        )

        self.assertIn(
            'href="http://localhost:5173/reset-password/',
            html_content,
        )