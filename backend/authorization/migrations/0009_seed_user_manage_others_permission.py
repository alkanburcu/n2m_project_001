from django.db import migrations


PERMISSION_KEY = "users.manage_others"


def seed_permission(apps, schema_editor):
    Permission = apps.get_model(
        "authorization",
        "Permission",
    )

    Permission.objects.update_or_create(
        key=PERMISSION_KEY,
        defaults={
            "name": "Manage other users",
            "description": (
                "Allows profile operations "
                "on other users."
            ),
            "is_active": True,
        },
    )


def remove_permission(apps, schema_editor):
    Permission = apps.get_model(
        "authorization",
        "Permission",
    )

    Permission.objects.filter(
        key=PERMISSION_KEY,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
    (
        "authorization",
        "0008_seed_company_permissions",
    ),
]

    operations = [
        migrations.RunPython(
            seed_permission,
            remove_permission,
        ),
    ]