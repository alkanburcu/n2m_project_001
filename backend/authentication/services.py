import secrets

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone


OTP_EXPIRATION_TIME = 600
OTP_RESEND_COOLDOWN = 60
OTP_MAX_ATTEMPTS = 5


def get_password_reset_cache_key(user_id):
    return f"password_reset:user:{user_id}"


def get_password_reset_cooldown_cache_key(user_id):
    return f"password_reset_cooldown:user:{user_id}"


def get_password_reset_code(user):
    cooldown_key = (
        get_password_reset_cooldown_cache_key(
            user.id,
        )
    )

    if not cache.add(
        cooldown_key,
        True,
        timeout=OTP_RESEND_COOLDOWN,
    ):
        return None

    code = (
        f"{secrets.randbelow(1000000):06d}"
    )

    cache_key = (
        get_password_reset_cache_key(
            user.id,
        )
    )

    expires_at = (
        timezone.now().timestamp()
        + OTP_EXPIRATION_TIME
    )

    cache.set(
        cache_key,
        {
            "user_id": str(user.id),
            "code_hash": make_password(code),
            "attempts": 0,
            "expires_at": expires_at,
        },
        timeout=OTP_EXPIRATION_TIME,
    )

    return code


def send_password_reset_email(
    user,
    code,
):
    subject = "Password Reset Request"

    message = (
        f"Your password reset code is: {code}.\n"
        "This code will expire in 10 minutes.\n\n"
        "If you did not request a password reset, "
        "please ignore this email."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )