
import logging
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


def send_simple_message(subject, text, sender, recipients, fail_silently=True):
    from django.core.mail import send_mail

    try:
        return send_mail(subject, text, sender, recipients)
    except SMTPException as e:
        print(e.message)
        if not fail_silently:
            raise e
        return 0
