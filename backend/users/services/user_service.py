from django.contrib.auth import get_user_model
from django.db import transaction

from authorization.services.assignments import assign_default_role

from ..models import UserEmail


User = get_user_model()


@transaction.atomic
def create_application_user(
    *,
    granted_by=None,
    **user_data,
):
    email = User.objects.normalize_email(
        user_data["email"].strip()
    )

    user_data["email"] = email

    user = User.objects.create_user(
        **user_data,
    )

    UserEmail.objects.create(
        user=user,
        email=email,
        is_primary=True,
        is_active=True,
    )

    assign_default_role(
        user=user,
        granted_by=granted_by,
    )

    return user