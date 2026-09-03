from django.db import migrations


POST_SCOPE_PERMISSIONS = {
    "posts.manage_others": "Manage Other Users' Posts",
}


def seed_post_scope_permissions(apps, schema_editor):
    Permission = apps.get_model(
        "authorization",
        "Permission",
    )

    for key, name in POST_SCOPE_PERMISSIONS.items():
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
        key__in=POST_SCOPE_PERMISSIONS.keys(),
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "authorization",
            "0005_add_todo_scope_permission",
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_post_scope_permissions,
            reverse_seed,
        ),
    ]