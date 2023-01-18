from datetime import datetime, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model

from .utils import send_reset_password_email, send_verification_email

User = get_user_model()


@shared_task()
def send_verification_email_task(
    user_id, receiver, current_site, mail_subject, email_template
):
    send_verification_email(
        user_id, receiver, current_site, mail_subject, email_template
    )
    return "Done"


@shared_task()
def send_reset_password_email_task(
    user_id, receiver, current_site, mail_subject, email_template
):
    send_reset_password_email(
        user_id, receiver, current_site, mail_subject, email_template
    )
    return "Done"


@shared_task
def delete_unverified_users():
    one_week_ago = datetime.now() - timedelta(days=7)
    unverified_users = User.objects.filter(
        created_date__lt=one_week_ago, is_verified=False
    )
    unverified_users.delete()
