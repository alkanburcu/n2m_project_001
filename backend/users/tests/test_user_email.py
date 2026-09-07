from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from users.services.user_service import create_application_user

from users.models import UserEmail


User = get_user_model()


class UserEmailTests(TestCase):
    def setUp(self):
        self.user01 = User.objects.create_user(
            username="user01",
            email="user01@test.com",
            password="Test123!",
        )

        self.user02 = User.objects.create_user(
            username="user02",
            email="user02@test.com",
            password="Test123!",
        )

    def test_user_can_have_multiple_emails(self):
        UserEmail.objects.create(
            user=self.user01,
            email="primary@test.com",
            is_primary=True,
        )

        UserEmail.objects.create(
            user=self.user01,
            email="secondary@test.com",
            is_primary=False,
        )

        self.assertEqual(
            self.user01.emails.count(),
            2,
        )

    def test_same_email_cannot_belong_to_multiple_users(
        self,
    ):
        UserEmail.objects.create(
            user=self.user01,
            email="shared@test.com",
            is_primary=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserEmail.objects.create(
                    user=self.user02,
                    email="shared@test.com",
                    is_primary=True,
                )

    def test_email_uniqueness_is_case_insensitive(
        self,
    ):
        UserEmail.objects.create(
            user=self.user01,
            email="Example@Test.com",
            is_primary=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserEmail.objects.create(
                    user=self.user02,
                    email="example@test.com",
                    is_primary=True,
                )

    def test_user_cannot_have_multiple_primary_emails(
        self,
    ):
        UserEmail.objects.create(
            user=self.user01,
            email="first@test.com",
            is_primary=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserEmail.objects.create(
                    user=self.user01,
                    email="second@test.com",
                    is_primary=True,
                )

    def test_different_users_can_each_have_primary_email(
        self,
    ):
        UserEmail.objects.create(
            user=self.user01,
            email="first@test.com",
            is_primary=True,
        )

        UserEmail.objects.create(
            user=self.user02,
            email="second@test.com",
            is_primary=True,
        )

        self.assertTrue(
            UserEmail.objects.filter(
                user=self.user01,
                is_primary=True,
            ).exists()
        )

        self.assertTrue(
            UserEmail.objects.filter(
                user=self.user02,
                is_primary=True,
            ).exists()
        )

    def test_application_user_creation_creates_primary_email(
        self,
    ):
        user = create_application_user(
            username="new_user",
            email="new_user@test.com",
            password="Test123!",
        )

        email_record = UserEmail.objects.get(
            user=user,
        )

        self.assertEqual(
            email_record.email,
            "new_user@test.com",
        )

        self.assertTrue(
            email_record.is_primary,
        )

        self.assertTrue(
            email_record.is_active,
        )