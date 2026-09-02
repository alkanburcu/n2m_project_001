from django.conf import settings
from django.db import migrations


def assign_standard_role_to_existing_users(apps, schema_editor):
    Role = apps.get_model(
        "authorization",
        "Role",
    )

    UserRoleAssignment = apps.get_model(
        "authorization",
        "UserRoleAssignment",
    )

    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(
        app_label,
        model_name,
    )

    standard_role = Role.objects.get(
        key="standard-user",
    )

    for user in User.objects.filter(
        is_superuser=False,
        is_active=True,
    ):
        UserRoleAssignment.objects.get_or_create(
            user=user,
            role=standard_role,
            is_active=True,
            defaults={
                "reason": "Default role assigned to existing user.",
            },
        )


def reverse_assignment(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("authorization", "0002_seed_user_permissions"),
    ]

    operations = [
        migrations.RunPython(
            assign_standard_role_to_existing_users,
            reverse_assignment,
        ),
    ]