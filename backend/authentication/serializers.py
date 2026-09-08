from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError

from authorization.services.resolver import get_effective_permissions
from rest_framework import serializers
from users.services.password_service import validate_new_password
from .services.password_reset_service import (
    PasswordResetLinkError,
    PasswordResetSessionError,
    get_password_reset_session_user,
    invalidate_password_reset_session,
    redeem_password_reset_link,
)


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
    )


class PasswordResetRequestSerializer(
    serializers.Serializer
):
    email = serializers.EmailField()

class PasswordResetRedeemSerializer(
    serializers.Serializer
):
    uid = serializers.CharField()
    token = serializers.CharField()

    def redeem(self):
        try:
            return redeem_password_reset_link(
                uid=self.validated_data["uid"],
                token=self.validated_data["token"],
            )

        except PasswordResetLinkError as error:
            raise serializers.ValidationError(
                "Invalid or expired "
                "password reset link."
            ) from error


class PasswordResetConfirmSerializer(
    serializers.Serializer
):
    reset_token = serializers.CharField(
        write_only=True,
    )

    new_password = serializers.CharField(
        write_only=True,
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        new_password = attrs[
            "new_password"
        ]

        new_password_confirm = attrs[
            "new_password_confirm"
        ]

        if (
            new_password
            != new_password_confirm
        ):
            raise serializers.ValidationError(
                {
                    "new_password_confirm": (
                        "Passwords do not match."
                    )
                }
            )

        try:
            user = (
                get_password_reset_session_user(
                    attrs["reset_token"]
                )
            )
        except PasswordResetSessionError as error:
            raise serializers.ValidationError(
                "Invalid or expired "
                "password reset session."
            ) from error

        try:
            validate_new_password(
                user=user,
                new_password=new_password,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {
                    "new_password": list(
                        error.messages
                    ),
                }
            ) from error

        attrs["user"] = user

        return attrs

    def save(self, **kwargs):
        user = self.validated_data[
            "user"
        ]

        reset_token = (
            self.validated_data[
                "reset_token"
            ]
        )

        new_password = (
            self.validated_data[
                "new_password"
            ]
        )

        user.set_password(
            new_password,
        )

        user.save(
            update_fields=["password"],
        )

        invalidate_password_reset_session(
            reset_token
        )

        return user

class CurrentUserSerializer(
    serializers.ModelSerializer
):
    email = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "is_superuser",
            "permissions",
        )

    def get_email(self, obj):
        email_record = (
            obj.emails
            .filter(
                is_primary=True,
                is_active=True,
            )
            .first()
        )

        if email_record is None:
            return None

        return email_record.email

    def get_permissions(self, obj):
        return get_effective_permissions(obj)