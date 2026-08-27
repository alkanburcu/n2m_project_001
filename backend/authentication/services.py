from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

def send_password_reset_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = f"{settings.FRONTEND_PASSWORD_RESET_URL}?uid64={uid}&token={token}"

    subject = "Password Reset Request"
    message = f"Hi {user.username},\n\nYou requested a password reset. Click the link below to reset your password:\n\n{reset_url}\n\nIf you didn't request this, please ignore this email."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)