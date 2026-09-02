from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from core.core_models import BaseModel


class Permission(BaseModel):
    key = models.CharField(max_length=150,unique=True,)

    name = models.CharField(max_length=100,)

    description = models.TextField(blank=True,)

    def __str__(self):
        return self.key


class Role(BaseModel):
    key = models.SlugField(max_length=100,unique=True,)

    name = models.CharField( max_length=100,)

    description = models.TextField(blank=True,)

    is_system = models.BooleanField(default=False,)

    def __str__(self):
        return self.name


class RolePermission(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE,related_name="role_permissions",)

    permission = models.ForeignKey(Permission,on_delete=models.CASCADE,related_name="role_permissions",)

    allowed = models.BooleanField(default=True,)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["role", "permission"],name="unique_role_permission",),
        ]

    def __str__(self):
        return f"{self.role.key} -> {self.permission.key}"


class UserRoleAssignment(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="role_assignments",)

    role = models.ForeignKey( Role,on_delete=models.CASCADE,related_name="user_assignments",)

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_role_assignments",
    )

    valid_from = models.DateTimeField(default=timezone.now,)

    valid_until = models.DateTimeField(null=True,blank=True,)

    revoked_at = models.DateTimeField(null=True,blank=True,)

    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revoked_role_assignments",
    )

    reason = models.TextField(blank=True,)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "role"],condition=Q(is_active=True),name="unique_active_user_role",),

            models.CheckConstraint(
                condition=(
                    Q(valid_until__isnull=True)
                    | Q(valid_until__gt=models.F("valid_from"))
                ),
                name="role_assignment_valid_dates",
            ),
        ]

        indexes = [
            models.Index(fields=["user", "is_active"],),
            models.Index(fields=["role", "is_active"],),
            models.Index(fields=["valid_until"],),
        ]

    def __str__(self):
        return f"{self.user} -> {self.role.key}"


class UserPermissionOverride(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="permission_overrides",
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="user_overrides",
    )

    allowed = models.BooleanField()

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_permission_overrides",
    )

    valid_from = models.DateTimeField( default=timezone.now,)

    valid_until = models.DateTimeField(null=True,blank=True,)

    revoked_at = models.DateTimeField(null=True,blank=True,)

    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revoked_permission_overrides",
    )

    reason = models.TextField(blank=True,)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "permission"],
                condition=Q(is_active=True),
                name="unique_active_user_permission_override",
            ),
            models.CheckConstraint(
                condition=(
                    Q(valid_until__isnull=True)
                    | Q(valid_until__gt=models.F("valid_from"))
                ),
                name="user_permission_valid_date_range",
            ),
        ]

        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["permission", "is_active"]),
            models.Index(fields=["valid_until"]),
        ]

    def __str__(self):
        return (
            f"{self.user} -> "
            f"{self.permission.key}: {self.allowed}"
        )