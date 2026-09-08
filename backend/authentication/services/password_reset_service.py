import hashlib
import secrets
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)

from users.models import UserEmail


User = get_user_model()


class PasswordResetLinkError(Exception):
    pass


class PasswordResetSessionError(Exception):
    pass


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


def _hash_value(value):
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _consumed_link_cache_key(uid, token):
    fingerprint = _hash_value(
        f"{uid}:{token}"
    )

    return (
        f"password_reset:"
        f"consumed:{fingerprint}"
    )


def _session_cache_key(reset_token):
    fingerprint = _hash_value(
        reset_token
    )

    return (
        f"password_reset:"
        f"session:{fingerprint}"
    )


def _password_fingerprint(user):
    return _hash_value(
        user.password
    )


def _get_user_from_reset_link(uid, token):
    try:
        user_id = force_str(
            urlsafe_base64_decode(uid)
        )

        user = User.objects.get(
            pk=user_id,
            is_active=True,
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ) as error:
        raise PasswordResetLinkError from error

    if not default_token_generator.check_token(
        user,
        token,
    ):
        raise PasswordResetLinkError

    return user


def redeem_password_reset_link(uid, token):
    user = _get_user_from_reset_link(
        uid,
        token,
    )

    consumed_key = (
        _consumed_link_cache_key(
            uid,
            token,
        )
    )

    was_added = cache.add(
        consumed_key,
        True,
        timeout=settings.PASSWORD_RESET_TIMEOUT,
    )

    if not was_added:
        raise PasswordResetLinkError

    reset_token = secrets.token_urlsafe(32)

    session_key = _session_cache_key(
        reset_token
    )

    cache.set(
        session_key,
        {
            "user_id": str(user.pk),
            "password_fingerprint": (
                _password_fingerprint(user)
            ),
        },
        timeout=(
            settings
            .PASSWORD_RESET_SESSION_TIMEOUT
        ),
    )

    return reset_token


def get_password_reset_session_user(
    reset_token,
):
    if not reset_token:
        raise PasswordResetSessionError

    session_key = _session_cache_key(
        reset_token
    )

    session_data = cache.get(
        session_key
    )

    if not session_data:
        raise PasswordResetSessionError

    try:
        user = User.objects.get(
            pk=session_data["user_id"],
            is_active=True,
        )
    except (
        KeyError,
        User.DoesNotExist,
    ) as error:
        cache.delete(session_key)
        raise PasswordResetSessionError from error

    expected_fingerprint = (
        session_data.get(
            "password_fingerprint"
        )
    )

    current_fingerprint = (
        _password_fingerprint(user)
    )

    if (
        not expected_fingerprint
        or expected_fingerprint
        != current_fingerprint
    ):
        cache.delete(session_key)
        raise PasswordResetSessionError

    return user


def invalidate_password_reset_session(
    reset_token,
):
    cache.delete(
        _session_cache_key(
            reset_token
        )
    )
