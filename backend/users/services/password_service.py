from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def validate_new_password(*, user, new_password):
    if user.check_password(new_password):
        raise ValidationError(
            "New password cannot be the same as the current password.",
            code="password_unchanged",
        )

    validate_password(
        password=new_password,
        user=user,
    )