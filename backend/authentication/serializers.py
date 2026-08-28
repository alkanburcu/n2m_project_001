from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers 

from .services import (OTP_MAX_ATTEMPTS, OTP_EXPIRATION_TIME, get_password_reset_cache_key)

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):

    email = serializers.EmailField()
    code = serializers.RegexField(regex=r'^\d{6}$')  # 6-digit code
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
       email = attrs["email"].lower()
       code = attrs["code"]
       new_password = attrs.get("new_password")

       user = User.objects.filter(email__iexact=email, is_active=True).first()
       if not user:
           raise serializers.ValidationError("User with this email does not exist.")
       cache_key = get_password_reset_cache_key(email)
       reset_data = cache.get(cache_key)

       if not reset_data:
              raise serializers.ValidationError("Invalid or expired password reset code.")

       if reset_data["attempts"] >= OTP_MAX_ATTEMPTS:
           cache.delete(cache_key)  # Clear the cache after exceeding attempts
           raise serializers.ValidationError("Maximum attempts exceeded. Please request a new password reset code.")

       remaining_time = int(reset_data["expires_at"]- timezone.now().timestamp())
       if remaining_time <= 0:
        cache.delete(cache_key)
        raise serializers.ValidationError("Invalid or expired password reset code.")

       if reset_data["attempts"] >= OTP_MAX_ATTEMPTS:
            cache.delete(cache_key)
            raise serializers.ValidationError("Maximum attemps exceed.\n\nPLease request a new reset code.")

       if not check_password(code, reset_data["code_hash"]):
           reset_data["attempts"] +=1
           if reset_data["attempts"] >= OTP_MAX_ATTEMPTS:
               cache.delete(cache_key)
           else:
               cache.set(cache_key, reset_data, timeout=remaining_time)
           raise serializers.ValidationError("Invalid password reset code.")
           
       try:
           validate_password(new_password, user)
       except DjangoValidationError as e:
              raise serializers.ValidationError({"new_password": list(e.messages)})
       attrs["user"] = user
       attrs["cache_key"] = cache_key
       return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save(update_fields=["password"])
        cache.delete(self.validated_data["cache_key"])  # Clear the cache after successful password reset

        return user