from django.db import migrations


CONTENT_PERMISSIONS = {
    # Todos
    "todos.list": "List Todos",
    "todos.view": "View Todo",
    "todos.create": "Create Todo",
    "todos.update": "Update Todo",
    "todos.delete": "Delete Todo",

    # Posts
    "posts.list": "List Posts",
    "posts.view": "View Post",
    "posts.create": "Create Post",
    "posts.update": "Update Post",
    "posts.delete": "Delete Post",

    # Comments
    "comments.list": "List Comments",
    "comments.view": "View Comment",
    "comments.create": "Create Comment",
    "comments.update": "Update Comment",
    "comments.delete": "Delete Comment",

    # Albums
    "albums.list": "List Albums",
    "albums.view": "View Album",
    "albums.create": "Create Album",
    "albums.update": "Update Album",
    "albums.delete": "Delete Album",

    # Photos
    "photos.list": "List Photos",
    "photos.view": "View Photo",
    "photos.create": "Create Photo",
    "photos.update": "Update Photo",
    "photos.delete": "Delete Photo",
}


def seed_content_permissions(apps, schema_editor):
    Permission = apps.get_model("authorization","Permission",)

    Role = apps.get_model("authorization","Role",)

    RolePermission = apps.get_model("authorization","RolePermission",)

    standard_role = Role.objects.get(key="standard-user",)

    for key, name in CONTENT_PERMISSIONS.items():
        permission, _ = Permission.objects.get_or_create(key=key,
            defaults={"name": name,"description": "",},
        )

        RolePermission.objects.get_or_create(
            role=standard_role,
            permission=permission,
            defaults={"allowed": True,},
        )


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("authorization", "0003_seed_user_authorization"),
    ]

    operations = [
        migrations.RunPython(seed_content_permissions, reverse_seed,),
    ]