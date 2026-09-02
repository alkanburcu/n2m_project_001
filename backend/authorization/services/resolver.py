from django.db.models import Q
from django.utils import timezone

from authorization.models import (
    Permission,
    RolePermission,
    UserPermissionOverride,
    UserRoleAssignment,
)


def has_permission(user, permission_key, obj=None, context=None):
    """
    Return whether the user currently has the given permission.

    `obj` and `context` are intentionally accepted now so that
    object/scope based authorization can be added later without
    changing the public API.
    """

    if not user or not user.is_authenticated:
        return False

    if not user.is_active:
        return False

    # Django superuser is kept as a root / break-glass account.
    # Application roles should not depend on this flag.
    if user.is_superuser:
        return True

    now = timezone.now()

    permission = (Permission.objects.filter(key=permission_key,is_active=True,).first())

    if permission is None:
        return False

    override = (
        UserPermissionOverride.objects
        .filter(
            user=user,
            permission=permission,
            is_active=True,
            revoked_at__isnull=True,
            valid_from__lte=now,
        )
        .filter( Q(valid_until__isnull=True)| Q(valid_until__gt=now)).first()
    )

    if override is not None:
        return override.allowed

    active_role_ids = (
        UserRoleAssignment.objects
        .filter(
            user=user,
            is_active=True,
            revoked_at__isnull=True,
            role__is_active=True,
            valid_from__lte=now,
        )
        .filter(Q(valid_until__isnull=True)| Q(valid_until__gt=now))
        .values_list("role_id",flat=True, )
    )

    return RolePermission.objects.filter(
        role_id__in=active_role_ids,
        permission=permission,
        role__is_active=True,
        permission__is_active=True,
        is_active=True,
        allowed=True,
    ).exists()

def get_effective_permissions(user):
    if not user or not user.is_authenticated:
        return {}

    if not user.is_active:
        return {}

    permission_keys = Permission.objects.filter(
        is_active=True,).values_list("key", flat=True)

    return {
        key: has_permission(user, key)
        for key in permission_keys
    }