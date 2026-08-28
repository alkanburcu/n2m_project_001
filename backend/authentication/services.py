import secrets
from ast import If
from django.core.cache import cache 
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

OTP_EXPIRATION_TIME = 600  # OTP expiration time in seconds (10 minutes)
OTP_RESEND_COOLDOWN = 60  # OTP resend cooldown time in seconds (1 minute)
OTP_MAX_ATTEMPTS = 5  # Maximum number of OTP attempts

def get_password_reset_cache_key(email):
    return f"password_reset:{email.lower()}"

def get_password_reset_cooldown_cache_key(email):
    return f"password_reset_cooldown:{email.lower()}"

def get_password_reset_code(email):
    cooldown_key = get_password_reset_cooldown_cache_key(email)
    if cache.get(cooldown_key):
        return None  # Cooldown period is active, do not generate a new code
    code = secrets.randbelow(1000000)  # Generate a random 6-digit code
    cache_key = get_password_reset_cache_key(email)
    cache.set(cache_key, {"code_hash": make_password(str(code)), "attempts": 0}, timeout = OTP_EXPIRATION_TIME)  # Store the code
    cache.set(cooldown_key, True, timeout=OTP_RESEND_COOLDOWN)  # Set cooldown period
    return code

def send_password_reset_email(user, code):
    subject = "Password Reset Request"
    message = f"Your password reset code is: {code}.\nThis code will expire in 10 minutes.\n\nIf you did not request a password reset, please ignore this email."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)