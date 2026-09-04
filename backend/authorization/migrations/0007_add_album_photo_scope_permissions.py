from django.db import migrations


ALBUM_PHOTO_SCOPE_PERMISSIONS = {
    "albums.manage_others": "Manage Other Users' Albums",
    "photos.manage_others": "Manage Other Users' Photos",
}


def seed_album_photo_scope_permissions(apps, schema_editor):
    Permission = apps.get_model(
        "authorization",
        "Permission",
    )

    for key, name in ALBUM_PHOTO_SCOPE_PERMISSIONS.items():
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
        key__in=ALBUM_PHOTO_SCOPE_PERMISSIONS.keys(),
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "authorization",
            "0006_add_post_scope_permission",
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_album_photo_scope_permissions,
            reverse_seed,
        ),
    ]