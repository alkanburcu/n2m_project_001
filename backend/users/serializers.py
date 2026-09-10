from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from .services.password_service import validate_new_password
from .services.user_service import create_application_user
from .models import Adress, geo, UserEmail
from rest_framework import serializers

from companies.models import Company
from companies.serializers import CompanySerializer

from django.conf import settings

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField( write_only=True, trim_whitespace=False, style={"input_type": "password"},)
    password_confirm = serializers.CharField( write_only=True, trim_whitespace=False, style={"input_type": "password"},)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password_confirm",)
        read_only_fields = ("id",)

    def validate_email(self, value):
        email = value.strip()

        if UserEmail.objects.filter(
            email__iexact=email,
        ).exists():
            raise serializers.ValidationError(
                "This email is already associated with an account."
            )

        return email

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError({ "password_confirm": ("Password fields do not match.")})

        candidate_user = User(username=attrs.get("username"),
                              email=attrs.get("email"), )

        try:
            validate_password(password=password,
                              user=candidate_user,)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"password": list(error.messages)}
            ) from error

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        request = self.context.get("request")

        granted_by = None

        if (
            request
            and request.user
            and request.user.is_authenticated
        ):
            granted_by = request.user

        return create_application_user(
            granted_by=granted_by,
            **validated_data,
        )


class GeoSerializer(serializers.ModelSerializer):
    class Meta:
        model = geo
        fields = ("lat", "lng")


class AddressSerializer(serializers.ModelSerializer):
    geo = GeoSerializer(read_only=True)

    class Meta:
        model = Adress
        fields = ("street","suite","city","zipcode","geo",)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True,)

    addresses = AddressSerializer(
        read_only=True,
    )

    company = CompanySerializer(
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "username",
            "first_name",
            "last_name",
            "display_name",
            "email",
            "phone_number",
            "website",
            "location",
            "profile_photo",
            "addresses",
            "company",
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
    
class ChangePasswordSerializer(
    serializers.Serializer
):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        user = self.context["request"].user

        current_password = attrs[
            "current_password"
        ]

        new_password = attrs[
            "new_password"
        ]

        new_password_confirm = attrs[
            "new_password_confirm"
        ]

        if not user.check_password(
            current_password
        ):
            raise serializers.ValidationError(
                {
                    "current_password": (
                        "Current password is incorrect."
                    )
                }
            )

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
            validate_new_password(
                user=user,
                new_password=new_password,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {
                    "new_password": list(
                        error.messages
                    )
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
            new_password
        )

        user.save(
            update_fields=["password"]
        )

        return user

class UserProfileUpdateSerializer(
    serializers.ModelSerializer
):
    company_id = serializers.PrimaryKeyRelatedField(
        source="company",
        queryset=Company.objects.filter(
            is_active=True,
        ),
        required=False,
        allow_null=True,
        write_only=True,
    )

    profile_photo = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "location",
            "website",
            "profile_photo",
            "company_id",
        )

    def validate_profile_photo(self, value):
        if value is None:
            return value

        max_size = (
            settings.PROFILE_PHOTO_MAX_SIZE_MB
            * 1024
            * 1024
        )

        if value.size > max_size:
            raise serializers.ValidationError(
                (
                    "Profile photo must not exceed "
                    f"{settings.PROFILE_PHOTO_MAX_SIZE_MB} MB."
                )
            )

        return value