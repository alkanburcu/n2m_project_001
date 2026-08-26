from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField( write_only=True, trim_whitespace=False, style={"input_type": "password"},)
    password_confirm = serializers.CharField( write_only=True, trim_whitespace=False, style={"input_type": "password"},)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password_confirm",)
        read_only_fields = ("id",)

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError({ "password_confirm": ("Password fields do not match.")})

        candidate_user = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
        )

        try:
            validate_password(
                password=password,
                user=candidate_user,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"password": list(error.messages)}
            ) from error

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        return User.objects.create_user(
            **validated_data
        )