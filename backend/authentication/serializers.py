from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from authorization.services.resolver import get_effective_permissions

from rest_framework import serializers 

from .services import (OTP_MAX_ATTEMPTS, OTP_EXPIRATION_TIME, get_password_reset_cache_key)

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class PasswordResetRequestSerializer(
    serializers.Serializer
):
    username = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, attrs):
        username = (
            attrs["username"].strip()
        )

        email = (
            attrs["email"]
            .strip()
            .lower()
        )

        user = User.objects.filter(
            username=username,
            email__iexact=email,
            is_active=True,
        ).first()

        attrs["username"] = username
        attrs["email"] = email
        attrs["user"] = user

        return attrs

class PasswordResetConfirmSerializer(
    serializers.Serializer
):
    username = serializers.CharField()

    email = serializers.EmailField()

    code = serializers.RegexField(
        regex=r"^\d{6}$",
    )

    new_password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        username = (
            attrs["username"].strip()
        )

        email = (
            attrs["email"]
            .strip()
            .lower()
        )

        code = attrs["code"]

        new_password = (
            attrs["new_password"]
        )

        user = User.objects.filter(
            username=username,
            email__iexact=email,
            is_active=True,
        ).first()

        if user is None:
            raise serializers.ValidationError(
                "Invalid or expired "
                "password reset code."
            )

        cache_key = (
            get_password_reset_cache_key(
                user.id,
            )
        )

        reset_data = cache.get(
            cache_key,
        )

        if not reset_data:
            raise serializers.ValidationError(
                "Invalid or expired "
                "password reset code."
            )

        if (
            str(
                reset_data.get(
                    "user_id",
                )
            )
            != str(user.id)
        ):
            cache.delete(cache_key)

            raise serializers.ValidationError(
                "Invalid or expired "
                "password reset code."
            )

        if (
            reset_data["attempts"]
            >= OTP_MAX_ATTEMPTS
        ):
            cache.delete(cache_key)

            raise serializers.ValidationError(
                "Maximum attempts exceeded. "
                "Please request a new "
                "password reset code."
            )

        expires_at = reset_data.get(
            "expires_at",
        )

        if expires_at is None:
            cache.delete(cache_key)

            raise serializers.ValidationError(
                "Invalid or expired "
                "password reset code."
            )

        remaining_time = int(
            expires_at
            - timezone.now().timestamp()
        )

        if remaining_time <= 0:
            cache.delete(cache_key)

            raise serializers.ValidationError(
                "Invalid or expired "
                "password reset code."
            )

        if not check_password(
            code,
            reset_data["code_hash"],
        ):
            reset_data["attempts"] += 1

            if (
                reset_data["attempts"]
                >= OTP_MAX_ATTEMPTS
            ):
                cache.delete(cache_key)
            else:
                cache.set(
                    cache_key,
                    reset_data,
                    timeout=remaining_time,
                )

            raise serializers.ValidationError(
                "Invalid password reset code."
            )

        try:
            validate_password(
                new_password,
                user,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {
                    "new_password":
                        list(error.messages),
                }
            )

        attrs["user"] = user
        attrs["cache_key"] = cache_key

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

        cache.delete(
            self.validated_data[
                "cache_key"
            ]
        )

        return user

class CurrentUserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id","username","email","is_superuser","permissions",)

    def get_permissions(self, obj):
        return get_effective_permissions(obj)