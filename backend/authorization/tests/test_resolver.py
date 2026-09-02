from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone

from authorization.models import (
    Permission,
    Role,
    RolePermission,
    UserPermissionOverride,
    UserRoleAssignment,
)
from authorization.services.resolver import (
    get_effective_permissions,
    has_permission,
)


User = get_user_model()

TEST_PERMISSION_KEY = "test.resolver.update"


class PermissionResolverTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="normaluser",
            email="normal@example.com",
            password="testpassword",
        )

        self.permission = Permission.objects.create(
            key=TEST_PERMISSION_KEY,
            name="Resolver Test Permission",
        )

        self.role = Role.objects.create(
            key="todo-manager",
            name="Todo Manager",
        )

    def assign_role(self, user=None, role=None, **kwargs):
        return UserRoleAssignment.objects.create(
            user=user or self.user,
            role=role or self.role,
            **kwargs,
        )

    def grant_permission(
        self,
        role=None,
        permission=None,
        allowed=True,
    ):
        return RolePermission.objects.create(
            role=role or self.role,
            permission=permission or self.permission,
            allowed=allowed,
        )

    def test_anonymous_user_is_denied(self):
        user = AnonymousUser()

        self.assertFalse(
            has_permission(
                user,
                self.permission.key,
            )
        )

    def test_inactive_user_is_denied(self):
        self.user.is_active = False
        self.user.save()

        self.assign_role()
        self.grant_permission()

        self.assertFalse(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_unknown_permission_is_denied(self):
        self.assertFalse(
            has_permission(
                self.user,
                "something.that.does.not.exist",
            )
        )

    def test_role_can_grant_permission(self):
        self.assign_role()
        self.grant_permission()

        self.assertTrue(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_role_permission_with_allowed_false_does_not_grant(self):
        self.assign_role()
        self.grant_permission(
            allowed=False,
        )

        self.assertFalse(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_inactive_role_does_not_grant_permission(self):
        self.role.is_active = False
        self.role.save()

        self.assign_role()
        self.grant_permission()

        self.assertFalse(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_inactive_role_assignment_does_not_grant_permission(self):
        self.assign_role(
            is_active=False,
        )
        self.grant_permission()

        self.assertFalse(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_revoked_role_assignment_does_not_grant_permission(self):
        self.assign_role(
            revoked_at=timezone.now(),
        )
        self.grant_permission()

        self.assertFalse(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_expired_role_assignment_does_not_grant_permission(self):
        now = timezone.now()

        self.assign_role(
            valid_from=now - timedelta(days=10),
            valid_until=now - timedelta(days=1),
        )
        self.grant_permission()

        self.assertFalse(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_future_role_assignment_does_not_grant_permission(self):
        now = timezone.now()

        self.assign_role(
            valid_from=now + timedelta(days=1),
            valid_until=now + timedelta(days=10),
        )
        self.grant_permission()

        self.assertFalse(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_user_override_can_grant_permission(self):
        UserPermissionOverride.objects.create(
            user=self.user,
            permission=self.permission,
            allowed=True,
        )

        self.assertTrue(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_user_deny_override_wins_over_role_grant(self):
        self.assign_role()
        self.grant_permission()

        UserPermissionOverride.objects.create(
            user=self.user,
            permission=self.permission,
            allowed=False,
        )

        self.assertFalse(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_expired_override_is_ignored(self):
        self.assign_role()
        self.grant_permission()

        now = timezone.now()

        UserPermissionOverride.objects.create(
            user=self.user,
            permission=self.permission,
            allowed=False,
            valid_from=now - timedelta(days=10),
            valid_until=now - timedelta(days=1),
        )

        self.assertTrue(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_multiple_roles_allow_if_one_role_grants_permission(self):
        second_role = Role.objects.create(
            key="second-role",
            name="Second Role",
        )

        self.assign_role(
            role=self.role,
        )
        self.assign_role(
            role=second_role,
        )

        self.grant_permission(
            role=self.role,
            allowed=False,
        )

        self.grant_permission(
            role=second_role,
            allowed=True,
        )

        self.assertTrue(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_inactive_permission_is_denied(self):
        self.permission.is_active = False
        self.permission.save()

        self.assign_role()
        self.grant_permission()

        self.assertFalse(
            has_permission(
                self.user,
                self.permission.key,
            )
        )

    def test_superuser_is_allowed(self):
        superuser = User.objects.create_superuser(
            username="rootuser",
            email="root@example.com",
            password="testpassword",
        )

        self.assertTrue(
            has_permission(
                superuser,
                "authorization.anything",
            )
        )

    def test_effective_permissions_include_active_permissions(self):
        view_permission = Permission.objects.create(
            key="test.resolver.view",
            name="Resolver View Permission",
        )

        self.assign_role()

        self.grant_permission(
            permission=self.permission,
            allowed=True,
        )

        self.grant_permission(
            permission=view_permission,
            allowed=False,
        )

        permissions = get_effective_permissions(
            self.user
        )

        self.assertEqual(
            permissions[self.permission.key],
            True,
        )

        self.assertEqual(
            permissions[view_permission.key],
            False,
        )

    def test_effective_permissions_respect_user_override(self):
        self.assign_role()
        self.grant_permission()

        UserPermissionOverride.objects.create(
            user=self.user,
            permission=self.permission,
            allowed=False,
        )

        permissions = get_effective_permissions(
            self.user
        )

        self.assertFalse(
            permissions[self.permission.key]
        )

    def test_effective_permissions_exclude_inactive_permissions(self):
        self.permission.is_active = False
        self.permission.save()

        permissions = get_effective_permissions(
            self.user
        )

        self.assertNotIn(
            self.permission.key,
            permissions,
        )

    def test_effective_permissions_for_inactive_user_are_empty(self):
        self.user.is_active = False
        self.user.save()

        permissions = get_effective_permissions(
            self.user
        )

        self.assertEqual(
            permissions,
            {},
        )

    def test_effective_permissions_for_superuser_allow_all_active_permissions(self):
        extra_permission = Permission.objects.create(
            key="test.extra_permission",
            name="Test Extra Permission",
        )

        superuser = User.objects.create_superuser(
            username="effective-root",
            email="effective-root@example.com",
            password="testpassword",
        )

        permissions = get_effective_permissions(
            superuser
        )

        self.assertTrue(
            permissions[self.permission.key]
        )

        self.assertTrue(
            permissions[extra_permission.key]
        )