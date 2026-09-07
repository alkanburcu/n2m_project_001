from django.db import migrations


def migrate_user_emails(apps, schema_editor):
    User = apps.get_model("users", "User")
    UserEmail = apps.get_model("users", "UserEmail")

    users = (
        User.objects
        .exclude(email__isnull=True)
        .exclude(email="")
    )

    for user in users.iterator():
        email = user.email.strip()

        if not email:
            continue

        UserEmail.objects.create(
            user_id=user.pk,
            email=email,
            is_primary=True,
            is_active=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_useremail"),
    ]

    operations = [
        migrations.RunPython(
            migrate_user_emails,
            migrations.RunPython.noop,
        ),
    ]