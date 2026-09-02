from django.db import migrations


USER_PERMISSIONS = {
    "users.list": "List Users",
    "users.view": "View User",
    "users.create": "Create User",
    "users.update": "Update User",
    "users.delete": "Delete User",
}


def seed_user_permissions(apps, schema_editor):
    Permission = apps.get_model("authorization", "Permission")
    Role = apps.get_model("authorization", "Role")
    RolePermission = apps.get_model(
        "authorization",
        "RolePermission",
    )

    for key, name in USER_PERMISSIONS.items():
        Permission.objects.get_or_create(
            key=key,
            defaults={
                "name": name,
                "description": "",
            },
        )

    standard_user_role, _ = Role.objects.get_or_create(
        key="standard-user",
        defaults={
            "name": "Standard User",
            "description": "Default application user.",
        },
    )

    for key in ("users.view","users.update",):
        permission = Permission.objects.get(key=key)

        RolePermission.objects.get_or_create(
            role=standard_user_role,
            permission=permission,
            defaults={
                "allowed": True,
            },
        )


def reverse_seed(apps, schema_editor):
    # We deliberately do not delete authorization data on reverse migration to avoid accidental data loss. 
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("authorization", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_user_permissions,reverse_seed,),
    ]