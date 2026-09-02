from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authorization.services.assignments import assign_default_role

from posts.models import Comment, Post


User = get_user_model()


class CommentPermissionTests(APITestCase):
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
            title="Test Post",
            body="Test body",
        )

        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user02,
            body="User02 comment",
        )

        assign_default_role(user=self.user01)
        assign_default_role(user=self.user02)

    def test_user_can_comment_on_another_users_post(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.post(
            reverse("comment-list"),
            {
                "post": str(self.post.id),
                "body": "New comment",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user01.id)

    def test_other_user_cannot_update_comment(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.patch(
            reverse("comment-detail", args=[self.comment.id]),
            {"body": "Changed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, "User02 comment")

    def test_owner_can_delete_comment(self):
        self.client.force_authenticate(user=self.user02)

        response = self.client.delete(
            reverse("comment-detail", args=[self.comment.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Comment.objects.filter(id=self.comment.id).exists()
        )

    def test_superuser_can_update_any_comment(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.patch(
            reverse("comment-detail", args=[self.comment.id]),
            {"body": "Admin updated"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, "Admin updated")