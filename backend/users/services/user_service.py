from django.contrib.auth import get_user_model
from django.db import transaction

from authorization.services.assignments import assign_default_role


User = get_user_model()


@transaction.atomic
def create_application_user(
    *,
    granted_by=None,
    **user_data,
):
    user = User.objects.create_user(
        **user_data,
    )

    assign_default_role(
        user=user,
        granted_by=granted_by,
    )

    return user