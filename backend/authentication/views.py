from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, CurrentUserSerializer

from .services.email_service import (send_password_reset_link_email,)
from .services.password_reset_service import (generate_password_reset_link,get_active_user_email,)

from users.serializers import UserCreateSerializer

User = get_user_model()


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Authentication successful
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }, status=status.HTTP_200_OK)
            else:
                # Authentication failed
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        email = serializer.validated_data[
            "email"
        ]

        email_record = get_active_user_email(
            email,
        )

        if email_record is not None:
            user = email_record.user

            reset_link = (
                generate_password_reset_link(
                    user,
                )
            )

            send_password_reset_link_email(
                email=email_record.email,
                reset_link=reset_link,
            )

        return Response(
            {
                "message": (
                    "If an account exists for "
                    "this email, a password "
                    "reset link has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )
    
class PasswordResetConfirmView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            {
                "message": (
                    "Password reset successful"
                )
            },
            status=status.HTTP_200_OK,
        )

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserCreateSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        user = serializer.save()

        primary_email = user.emails.get(
            is_primary=True,
            is_active=True,
        )

        return Response(
            {
                "message": (
                    "User registered successfully"
                ),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": primary_email.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)