from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authorization.services.assignments import assign_default_role
from authorization.models import (
    Permission,
    UserPermissionOverride,
)
from albums.models import Album
from posts.models import Post
from todos.models import Todo

User = get_user_model()


class UserPermissionTests(APITestCase):
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

        assign_default_role(user=self.user01)
        assign_default_role(user=self.user02)

        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="Admin123!",
        )
        self.manage_others_permission = (
            Permission.objects.get(
                key="users.manage_others",
            )
        )

    def test_unauthenticated_user_cannot_access_users(self):
        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_normal_user_cannot_list_users(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_normal_user_can_retrieve_user(self):
        self.client.force_authenticate(
            user=self.user01,
        )

        response = self.client.get(
            reverse(
                "user-detail",
                args=[self.user02.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(self.user02.id),
        )

    def test_normal_user_cannot_update_user(self):
        self.client.force_authenticate(
            user=self.user01,
        )

        response = self.client.patch(
            reverse(
                "user-detail",
                args=[self.user02.id],
            ),
            {
                "first_name": "Changed",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.user02.refresh_from_db()

        self.assertNotEqual(
            self.user02.first_name,
            "Changed",
        )

    def test_user_with_manage_others_can_update_user(
        self,
    ):
        UserPermissionOverride.objects.create(
            user=self.user01,
            permission=self.manage_others_permission,
            allowed=True,
        )

        self.client.force_authenticate(
            user=self.user01,
        )

        response = self.client.patch(
            reverse(
                "user-detail",
                args=[self.user02.id],
            ),
            {
                "first_name": "Updated",
                "location": "Ankara",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user02.refresh_from_db()

        self.assertEqual(
            self.user02.first_name,
            "Updated",
        )

        self.assertEqual(
            self.user02.location,
            "Ankara",
        )

    def test_normal_user_cannot_delete_user(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.delete(
            reverse(
                "user-detail",
                args=[self.user02.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            User.objects.filter(
                id=self.user02.id
            ).exists()
        )

    def test_superuser_can_list_users(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            3,
        )

    def test_superuser_can_retrieve_user(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.get(
            reverse(
                "user-detail",
                args=[self.user01.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(self.user01.id),
        )

        self.assertEqual(
            response.data["username"],
            "user01",
        )

    def test_superuser_can_update_user(self):
        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.patch(
            reverse(
                "user-detail",
                args=[self.user01.id],
            ),
            {
                "first_name": "Updated",
                "username": "should_not_change",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user01.refresh_from_db()

        self.assertEqual(
            self.user01.first_name,
            "Updated",
        )

        self.assertEqual(
            self.user01.username,
            "user01",
        )

    def test_superuser_can_delete_user(self):
        user_to_delete = User.objects.create_user(
            username="deleteuser",
            email="delete@test.com",
            password="Test123!",
        )

        self.client.force_authenticate(user=self.superuser,)

        response = self.client.delete(
            reverse("user-detail", args=[user_to_delete.id],)
        )

        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT,)

        self.assertTrue(
            User.objects.filter(id=user_to_delete.id,).exists()
        )

        user_to_delete.refresh_from_db()

        self.assertFalse(user_to_delete.is_active)

        response = self.client.get(
            reverse("user-detail", args=[user_to_delete.id],)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,)

    def test_soft_deleted_user_hides_related_content(
        self,
    ):
        todo = Todo.objects.create(
            user=self.user02,
            title="Preserved todo",
        )

        post = Post.objects.create(
            user=self.user02,
            title="Preserved post",
            body="Post body",
        )

        album = Album.objects.create(
            user=self.user02,
            title="Preserved album",
        )

        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.delete(
            reverse(
                "user-detail",
                args=[self.user02.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.user02.refresh_from_db()

        self.assertFalse(
            self.user02.is_active
        )

        self.assertTrue(
            Todo.objects.filter(id=todo.id).exists()
        )
        self.assertTrue(
            Post.objects.filter(id=post.id).exists()
        )
        self.assertTrue(
            Album.objects.filter(id=album.id).exists()
        )

        todo_response = self.client.get(
            reverse(
                "todo-detail",
                args=[todo.id],
            )
        )

        post_response = self.client.get(
            reverse(
                "post-detail",
                args=[post.id],
            )
        )

        album_response = self.client.get(
            reverse(
                "album-detail",
                args=[album.id],
            )
        )

        self.assertEqual(
            todo_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            post_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            album_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )