from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class RegisterTests(APITestCase):

    def setUp(self):
        self.url = reverse("register")

        self.valid_data = {
            "username": "test_user",
            "email": "test_user@test.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_data,)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,)

        self.assertTrue(
            User.objects.filter(username="test_user").exists())

        user = User.objects.get( username="test_user")

        self.assertEqual(user.email, "test_user@test.com",)

    def test_password_is_hashed(self):
        response = self.client.post(self.url, self.valid_data,)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,)

        user = User.objects.get(username="test_user")

        self.assertNotEqual(user.password, self.valid_data["password"],)

        self.assertTrue(user.check_password(self.valid_data["password"]))

    def test_password_mismatch(self):
        data = self.valid_data.copy()
        data["password_confirm"] = "DifferentPassword123."

        response = self.client.post(self.url,data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,)

        self.assertIn("password_confirm", response.data,)

        self.assertFalse(User.objects.filter(username="test_user").exists())

    def test_duplicate_username(self):
        User.objects.create_user(
            username="test_user",
            email="first@test.com",
            password="StrongPassword123!",
        )

        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

        self.assertIn("username",response.data,)

    def test_duplicate_email(self):
        User.objects.create_user(
            username="existing_user",
            email="test_user@test.com",
            password="StrongPassword123!",
        )

        response = self.client.post(self.url, self.valid_data,)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("email",response.data,)

    def test_weak_password(self):
        data = self.valid_data.copy()

        data["password"] = "123"
        data["password_confirm"] = "123"

        response = self.client.post(self.url,data,)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,)

        self.assertIn("password", response.data,)

        self.assertFalse(User.objects.filter(username="test_user").exists())

    def test_missing_username(self):
        data = self.valid_data.copy()
        data.pop("username")

        response = self.client.post(self.url,data)

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)

        self.assertIn("username",response.data,)

    def test_missing_email(self):
        data = self.valid_data.copy()
        data.pop("email")

        response = self.client.post(self.url,data,)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("email", response.data,)

    def test_missing_password(self):
        data = self.valid_data.copy()
        data.pop("password")

        response = self.client.post(self.url,data,)

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)
     

        self.assertIn("password",response.data,)

    def test_password_not_returned_in_response(self):
        response = self.client.post(self.url,self.valid_data,)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED,)

        self.assertNotIn("password",response.data,)

        self.assertNotIn("password_confirm",response.data,)

        self.assertNotIn( "password", response.data["user"],)

    def test_registered_user_gets_default_role(self):
        response = self.client.post(self.url,self.valid_data,format="json",)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED,)

        user = User.objects.get( username=self.valid_data["username"],)

        self.assertTrue(
            user.role_assignments.filter(role__key="standard-user",is_active=True,).exists()
        )

        