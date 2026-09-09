from django.db import migrations


COMPANY_PERMISSIONS = {
    "companies.list": "List Companies",
    "companies.view": "View Company",
    "companies.create": "Create Company",
    "companies.update": "Update Company",
    "companies.delete": "Delete Company",
}


STANDARD_USER_COMPANY_PERMISSIONS = {
    "companies.list",
    "companies.view",
    "companies.create",
}


def seed_company_permissions(apps, schema_editor):
    Permission = apps.get_model(
        "authorization",
        "Permission",
    )

    Role = apps.get_model(
        "authorization",
        "Role",
    )

    RolePermission = apps.get_model(
        "authorization",
        "RolePermission",
    )

    standard_role = Role.objects.get(
        key="standard-user",
    )

    for key, name in COMPANY_PERMISSIONS.items():
        permission, _ = Permission.objects.get_or_create(
            key=key,
            defaults={
                "name": name,
                "description": "",
            },
        )

        if key in STANDARD_USER_COMPANY_PERMISSIONS:
            RolePermission.objects.get_or_create(
                role=standard_role,
                permission=permission,
                defaults={
                    "allowed": True,
                },
            )


def reverse_seed(apps, schema_editor):
    Permission = apps.get_model(
        "authorization",
        "Permission",
    )

    RolePermission = apps.get_model(
        "authorization",
        "RolePermission",
    )

    permissions = Permission.objects.filter(
        key__in=COMPANY_PERMISSIONS.keys(),
    )

    RolePermission.objects.filter(
        permission__in=permissions,
    ).delete()

    permissions.delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "authorization",
            "0007_add_album_photo_scope_permissions",
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_company_permissions,
            reverse_seed,
        ),
    ]