from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authorization.services.assignments import assign_default_role

from posts.models import Post


User = get_user_model()


class PostPermissionTests(APITestCase):
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

        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="Admin123!",
        )

        self.post = Post.objects.create(
            user=self.user01,
            title="User01 Post",
            body="Post body",
        )

        assign_default_role(user=self.user01)
        assign_default_role(user=self.user02)

    def test_authenticated_user_can_read_other_users_posts(self):
        self.client.force_authenticate(user=self.user02)

        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_can_create_post_in_own_name(self):
        self.client.force_authenticate(user=self.user02)

        response = self.client.post(
            reverse("post-list"),
            {
                "title": "User02 Post",
                "body": "Hello",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user02.id)

    def test_owner_can_update_post(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.patch(
            reverse("post-detail", args=[self.post.id]),
            {"title": "Updated"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated")

    def test_other_user_cannot_update_post(self):
        self.client.force_authenticate(user=self.user02)

        response = self.client.patch(
            reverse("post-detail", args=[self.post.id]),
            {"title": "Hacked"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "User01 Post")

    def test_other_user_cannot_delete_post(self):
        self.client.force_authenticate(user=self.user02)

        response = self.client.delete(
            reverse("post-detail", args=[self.post.id])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Post.objects.filter(id=self.post.id).exists()
        )

    def test_owner_can_delete_post(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.delete(
            reverse("post-detail", args=[self.post.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Post.objects.filter(id=self.post.id).exists()
        )

    def test_superuser_can_update_any_post(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.patch(
            reverse("post-detail", args=[self.post.id]),
            {"title": "Admin Updated"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Admin Updated")