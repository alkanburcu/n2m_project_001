from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.models import UserEmail


def get_active_user_email(email):
    return (
        UserEmail.objects
        .select_related("user")
        .filter(
            email__iexact=email.strip(),
            is_active=True,
            user__is_active=True,
        )
        .first()
    )


def generate_password_reset_link(user):
    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    token = default_token_generator.make_token(
        user
    )

    reset_path = (
        f"reset-password/{uid}/{token}"
    )

    return urljoin(
        f"{settings.FRONTEND_BASE_URL.rstrip('/')}/",
        reset_path,
    )