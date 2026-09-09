import os
import tempfile
import uuid

from io import BytesIO

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from django.test import override_settings

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from authorization.services.assignments import (
    assign_default_role,
)
from companies.models import Company


User = get_user_model()


class UserProfileTests(APITestCase):
    def setUp(self):
        self.temp_media = (
            tempfile.TemporaryDirectory()
        )

        self.media_override = override_settings(
            MEDIA_ROOT=self.temp_media.name,
        )

        self.media_override.enable()

        self.addCleanup(
            self.media_override.disable
        )

        self.addCleanup(
            self.temp_media.cleanup
        )

        self.user = User.objects.create_user(
            username="user01",
            email="user01@test.com",
            password="Test123!",
        )

        assign_default_role(
            user=self.user,
        )

        self.company = Company.objects.create(
            name="N2Mobil",
            address="Ankara",
            city="Ankara",
            phone_number="03120000000",
            website="https://example.com",
        )

        self.url = reverse(
            "user-me"
        )

        self.client.force_authenticate(
            user=self.user,
        )

    def create_image(
        self,
        filename="profile.jpg",
        image_format="JPEG",
        size=(300, 300),
        content_type="image/jpeg",
    ):
        buffer = BytesIO()

        image = Image.new(
            "RGB",
            size,
        )

        image.save(
            buffer,
            format=image_format,
        )

        buffer.seek(0)

        return SimpleUploadedFile(
            filename,
            buffer.read(),
            content_type=content_type,
        )

    def test_user_can_get_own_profile(self):
        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            self.user.username,
        )

    def test_display_name_falls_back_to_username(self):
        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.data["display_name"],
            self.user.username,
        )

    def test_user_can_update_profile(self):
        response = self.client.patch(
            self.url,
            {
                "first_name": "Burcu",
                "last_name": "Alkan",
                "location": "Ankara, Türkiye",
                "website": "https://example.com",
                "company_id": str(
                    self.company.id
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "Burcu",
        )

        self.assertEqual(
            self.user.last_name,
            "Alkan",
        )

        self.assertEqual(
            self.user.location,
            "Ankara, Türkiye",
        )

        self.assertEqual(
            self.user.company,
            self.company,
        )

        self.assertEqual(
            response.data["display_name"],
            "Burcu Alkan",
        )

        self.assertEqual(
            response.data["company"]["name"],
            "N2Mobil",
        )

    def test_user_can_remove_company(self):
        self.user.company = self.company

        self.user.save(
            update_fields=["company"]
        )

        response = self.client.patch(
            self.url,
            {
                "company_id": None,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertIsNone(
            self.user.company
        )

    def test_invalid_company_is_rejected(self):
        response = self.client.patch(
            self.url,
            {
                "company_id": str(
                    uuid.uuid4()
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "company_id",
            response.data,
        )

    def test_profile_cannot_change_username(self):
        response = self.client.patch(
            self.url,
            {
                "username": "changed_username",
                "first_name": "Burcu",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.username,
            "user01",
        )

        self.assertEqual(
            self.user.first_name,
            "Burcu",
        )

    def test_user_can_upload_profile_photo(self):
        photo = self.create_image()

        response = self.client.patch(
            self.url,
            {
                "profile_photo": photo,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.profile_photo.name
        )

        self.assertTrue(
            os.path.exists(
                self.user.profile_photo.path
            )
        )

    @override_settings(
        PROFILE_PHOTO_MAX_SIZE_MB=1
    )
    def test_large_profile_photo_is_rejected(self):
        photo = self.create_image(
            filename="large.bmp",
            image_format="BMP",
            size=(1000, 1000),
            content_type="image/bmp",
        )

        response = self.client.patch(
            self.url,
            {
                "profile_photo": photo,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "profile_photo",
            response.data,
        )

    def test_unauthenticated_user_cannot_access_profile(
        self,
    ):
        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )