from django.db import migrations


TODO_SCOPE_PERMISSIONS = {
    "todos.manage_others": "Manage Other Users' Todos",
}


def seed_todo_scope_permissions(apps, schema_editor):
    Permission = apps.get_model(
        "authorization",
        "Permission",
    )

    for key, name in TODO_SCOPE_PERMISSIONS.items():
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
        key__in=TODO_SCOPE_PERMISSIONS.keys(),
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "authorization",
            "0004_seed_content_permissions",
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_todo_scope_permissions,
            reverse_seed,
        ),
    ]