from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from ecommerce.celery import app


@app.task
def send_order_email(subject, message, user_email):
    
    send_mail(
        subject=subject,
        message=strip_tags(message),
        recipient_list=[user_email],
        from_email=settings.DEFAULT_FROM_EMAIL,
    )
