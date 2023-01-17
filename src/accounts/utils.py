import threading

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.tokens import RefreshToken


class SendEmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self.email = email

    def run(self):
        self.email.send()


def send_verification_email(request, user, mail_subject, email_template):
    token = RefreshToken.for_user(user).access_token
    current_site = get_current_site(request)
    message = render_to_string(
        email_template,
        {
            "domain": current_site.domain,
            "token": token,
        },
    )
    email = EmailMessage(
        mail_subject, message, "mydjangoproject87@gmail.com", to=[user.email]
    )
    email.content_subtype = "html"
    SendEmailThread(email).start()


def send_reset_password_email(request, user, mail_subject, email_template):
    current_site = get_current_site(request)
    uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)
    message = render_to_string(
        email_template,
        {
            "domain": current_site.domain,
            "user": user,
            "token": token,
            "uid": uidb64,
        },
    )
    email = EmailMessage(
        mail_subject, message, "mydjangoproject87@gmail.com", to=[user.email]
    )
    email.content_subtype = "html"
    SendEmailThread(email).start()
