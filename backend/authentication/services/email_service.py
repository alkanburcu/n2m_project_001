from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_password_reset_link_email(
    *,
    email,
    reset_link,
):
    subject = "Reset your password"

    message = (
        "We received a request to reset your password.\n\n"
        "You can reset your password using the link below:\n"
        f"{reset_link}\n\n"
        "If you did not request this change, "
        "you can ignore this email."
    )

    html_message = render_to_string(
        "authentication/emails/password_reset.html",
        {
            "reset_link": reset_link,
        },
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )