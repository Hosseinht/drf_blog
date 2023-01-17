from celery import shared_task

from .utils import send_reset_password_email, send_verification_email


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
