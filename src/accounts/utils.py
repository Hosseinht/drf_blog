from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def send_verification_email(
    user_id, receiver, current_site, mail_subject, email_template
):
    user = User.objects.get(id=user_id)
    token = RefreshToken.for_user(user).access_token

    message = render_to_string(
        email_template,
        {
            "domain": current_site,
            "token": token,
        },
    )
    email = EmailMessage(
        mail_subject, message, "mydjangoproject87@gmail.com", to=[receiver]
    )
    email.content_subtype = "html"
    # SendEmailThread(email).start()
    email.send()


def send_reset_password_email(
    user_id, receiver, current_site, mail_subject, email_template
):
    user = User.objects.get(id=user_id)
    uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)
    message = render_to_string(
        email_template,
        {
            "domain": current_site,
            "user": user,
            "token": token,
            "uid": uidb64,
        },
    )
    email = EmailMessage(
        mail_subject, message, "mydjangoproject87@gmail.com", to=[receiver]
    )
    email.content_subtype = "html"
    # SendEmailThread(email).start()
    email.send()
