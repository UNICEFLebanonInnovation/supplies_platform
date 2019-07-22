
import logging
import requests
from django.conf import settings
from smtplib import SMTPException


def send_multi_message(subject, text, sender, recipients, fail_silently=True):
    from django.core.mail import EmailMultiAlternatives

    msg = EmailMultiAlternatives(subject, text,
                                 sender,
                                 recipients)
    try:
        return msg.send()
    except SMTPException as e:
        print(e.message)
        if not fail_silently:
            raise e
        return 0


def send_simple_message(subject, text, recipients, fail_silently=True):

    try:
        return requests.post(
            "https://api.mailgun.net/v3/sandboxb97bdf816375428bab2d69539eb1aed8.mailgun.org/messages",
            auth=("api", settings.MAILGUN_API_KEY),
            data={"from": "SMS Platform <sms@unicef.org>",
                  "to": recipients,
                  "subject": subject,
                  "text": text})

    except Exception as e:
        print(e.message)
        if not fail_silently:
            raise e
        return 0
