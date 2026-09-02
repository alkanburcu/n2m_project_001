from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from authorization.models import (
    Permission,
    Role,
    RolePermission,
    UserRoleAssignment,
)
from authorization.permissions import HasAppPermission


User = get_user_model()

TEST_PERMISSION_KEY = "test.has_app_permission.update"


class HasAppPermissionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="normaluser",
            email="normal@example.com",
            password="testpassword",
        )

        self.permission = Permission.objects.create(
            key=TEST_PERMISSION_KEY,
            name="Has App Permission Test",
        )

        self.role = Role.objects.create(
            key="test-permission-role",
            name="Test Permission Role",
        )

        self.permission_class = HasAppPermission()

    def make_view(self, action, permission_map=None):
        return SimpleNamespace(
            action=action,
            permission_map=permission_map or {},
        )

    def make_request(self, user):
        return SimpleNamespace(
            user=user,
        )

    def grant_permission(self):
        UserRoleAssignment.objects.create(
            user=self.user,
            role=self.role,
        )

        RolePermission.objects.create(
            role=self.role,
            permission=self.permission,
            allowed=True,
        )

    def test_mapped_action_is_allowed_when_user_has_permission(self):
        self.grant_permission()

        view = self.make_view(
            action="update",
            permission_map={
                "update": self.permission.key,
            },
        )

        request = self.make_request(
            self.user
        )

        self.assertTrue(
            self.permission_class.has_permission(
                request,
                view,
            )
        )

    def test_mapped_action_is_denied_without_permission(self):
        view = self.make_view(
            action="update",
            permission_map={
                "update": self.permission.key,
            },
        )

        request = self.make_request(
            self.user
        )

        self.assertFalse(
            self.permission_class.has_permission(
                request,
                view,
            )
        )

    def test_unmapped_action_is_denied(self):
        view = self.make_view(
            action="destroy",
            permission_map={
                "update": self.permission.key,
            },
        )

        request = self.make_request(
            self.user
        )

        self.assertFalse(
            self.permission_class.has_permission(
                request,
                view,
            )
        )

    def test_anonymous_user_is_denied(self):
        view = self.make_view(
            action="update",
            permission_map={
                "update": self.permission.key,
            },
        )

        request = self.make_request(
            AnonymousUser()
        )

        self.assertFalse(
            self.permission_class.has_permission(
                request,
                view,
            )
        )

    def test_object_permission_uses_same_permission_mapping(self):
        self.grant_permission()

        view = self.make_view(
            action="update",
            permission_map={
                "update": self.permission.key,
            },
        )

        request = self.make_request(
            self.user
        )

        self.assertTrue(
            self.permission_class.has_object_permission(
                request,
                view,
                object(),
            )
        )