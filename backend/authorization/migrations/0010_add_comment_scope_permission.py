from django.db import migrations


COMMENT_SCOPE_PERMISSIONS = {
    "comments.manage_others": "Manage Other Users' Comments",
}


def seed_comment_scope_permissions(apps, schema_editor):
    Permission = apps.get_model(
        "authorization",
        "Permission",
    )

    for key, name in COMMENT_SCOPE_PERMISSIONS.items():
        Permission.objects.get_or_create(
            key=key,
            defaults={
                "name": name,
                "description": "",
            },
        )


def reverse_seed(apps, schema_editor):
    Permission = apps.get_model(
        "authorization",
        "Permission",
    )

    Permission.objects.filter(
        key__in=COMMENT_SCOPE_PERMISSIONS.keys(),
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "authorization",
            "0009_seed_user_manage_others_permission",
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_comment_scope_permissions,
            reverse_seed,
        ),
    ]