from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from authorization.services.resolver import get_effective_permissions
from rest_framework import serializers
from users.services.password_service import validate_new_password


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


class PasswordResetConfirmSerializer(
    serializers.Serializer
):
    uid = serializers.CharField()
    token = serializers.CharField()

    new_password = serializers.CharField(
        write_only=True,
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        uid = attrs["uid"]
        token = attrs["token"]

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
        ):
            raise serializers.ValidationError(
                "Invalid or expired "
                "password reset link."
            )

        if not default_token_generator.check_token(
            user,
            token,
        ):
            raise serializers.ValidationError(
                "Invalid or expired "
                "password reset link."
            )

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