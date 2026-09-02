from django.db import transaction

from authorization.models import Role, UserRoleAssignment


class RoleAssignmentError(Exception):
    pass


@transaction.atomic
def assign_role(
    *,
    user,
    role,
    granted_by=None,
    reason="",
):
    if not role.is_active:
        raise RoleAssignmentError(
            "Inactive roles cannot be assigned."
        )

    existing_assignment = (
        UserRoleAssignment.objects
        .filter(
            user=user,
            role=role,
            is_active=True,
        )
        .first()
    )

    if existing_assignment:
        return existing_assignment

    return UserRoleAssignment.objects.create(
        user=user,
        role=role,
        granted_by=granted_by,
        reason=reason,
    )


def assign_default_role(
    *,
    user,
    granted_by=None,
):
    try:
        role = Role.objects.get(
            key="standard-user",
            is_active=True,
        )
    except Role.DoesNotExist as error:
        raise RoleAssignmentError(
            "Default application role is not configured."
        ) from error

    return assign_role(
        user=user,
        role=role,
        granted_by=granted_by,
        reason="Default role assigned on user creation.",
    )