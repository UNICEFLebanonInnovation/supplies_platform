import json
import httplib
import datetime

from time import mktime
from mailer import send_messaage


def send_notification(user_group, subject, obj, partner=None, recipient=None):
    from supplies_platform.backends.models import Notification

    instance = Notification.objects.create(
        subject=subject,
        user_group=user_group,
        partner=partner,
        send_to=recipient,
        object_id=obj.id,
        model=type(obj),
        description=obj.__unicode__(),
    )
    # send_messaage(subject, 'to do', 'sms@unicef.org', [recipient.email])
