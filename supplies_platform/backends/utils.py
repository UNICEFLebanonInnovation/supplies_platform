import json
import httplib
import datetime
import pyrebase

from time import mktime
from mailer import send_multi_message, send_simple_message
from supplies_platform.users.models import User


def send_notification(user_group, subject, obj, level='info', partner=None, recipient=None):
    from supplies_platform.backends.models import Notification

    instance = Notification.objects.create(
        subject=subject,
        user_group=user_group,
        partner_id=partner,
        send_to=recipient,
        object_id=obj.id,
        model=obj.__class__.__name__,
        description=obj.__unicode__(),
        level=level
    )

    config = {
        'apiKey': "AIzaSyA2Aio1bqRUXtYBZIe687hlgYR7lP2ETyQ",
        'authDomain': "supply-management-system.firebaseapp.com",
        'databaseURL': "https://supply-management-system.firebaseio.com",
        'projectId': "supply-management-system",
        'storageBucket': "supply-management-system.appspot.com",
        'messagingSenderId': "150092950355"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    data = {
        "subject": subject,
        "user_group": user_group,
        "partner": partner,
        "send_to": recipient,
        "object_id": obj.id,
        "model": obj.__class__.__name__,
        "description": obj.__unicode__(),
        "level": level
    }
    db.child("notifications").push(data)

    try:
        recipients = User.objects.filter(
            groups__name=user_group,
            section=obj.plan_section,
            email__isnull=False,
        ).values_list('email', flat=True).distinct()
        content = '{}: {}'.format(subject, obj.__unicode__())
        send_simple_message(subject, content, recipients)
    except Exception as ex:
        print(ex.message)
        pass
