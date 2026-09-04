from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authorization.services.assignments import assign_default_role

from todos.models import Todo


User = get_user_model()


class TodoPermissionTests(APITestCase):
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

        self.todo01 = Todo.objects.create(
            user=self.user01,
            title="User01 Todo",
            completed=False,
        )

        assign_default_role(user=self.user01)
        assign_default_role(user=self.user02)

    def test_user_can_create_own_todo(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.post(
            reverse("todo-list"),
            {
                "title": "New Todo",
                "completed": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user01.id)

    def test_user_only_sees_own_todos(self):
        Todo.objects.create(
            user=self.user02,
            title="User02 Todo",
            completed=False,
        )

        self.client.force_authenticate(user=self.user01)

        response = self.client.get(reverse("todo-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "User01 Todo")

    def test_owner_can_update_todo(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.patch(
            reverse("todo-detail", args=[self.todo01.id]),
            {"completed": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.todo01.refresh_from_db()
        self.assertTrue(self.todo01.completed)

    def test_other_user_cannot_update_todo(self):
        self.client.force_authenticate(user=self.user02)

        response = self.client.patch(
            reverse("todo-detail", args=[self.todo01.id]),
            {"completed": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_delete_todo(self):
        self.client.force_authenticate(user=self.user01)

        response = self.client.delete(
            reverse("todo-detail", args=[self.todo01.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Todo.objects.filter(id=self.todo01.id).exists()
        )

    def test_superuser_can_access_all_todos(self):
        Todo.objects.create(
            user=self.user02,
            title="User02 Todo",
            completed=False,
        )

        self.client.force_authenticate(user=self.superuser)

        response = self.client.get(reverse("todo-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_superuser_can_create_todo_for_another_user(self):
        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.post(
            reverse("todo-list"),
            {
                "user": str(self.user01.id),
                "title": "Created by admin",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            str(response.data["user"]),
            str(self.user01.id),
        )