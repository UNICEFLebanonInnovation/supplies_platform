import json
import httplib
import datetime
import pyrebase

from time import mktime
from mailer import send_multi_message, send_simple_message
from supplies_platform.users.models import User


def send_notification(user_group, subject, obj, tab='#general', level='info', partner=None, recipient=None):
    from supplies_platform.backends.models import Notification

    instance = Notification.objects.create(
        subject=subject,
        user_group=user_group,
        partner_id=partner,
        send_to=recipient,
        object_id=obj.id,
        model=obj.__class__.__name__,
        description=obj.__unicode__(),
        level=level,
        tab=tab
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
        content = '{}: {} \\r\\n Please click on the link: {}'.format(
            subject,
            obj.__unicode__(),
            obj.get_path(tab)
        )

        recipients = ['unicef.sms@gmail.com']
        send_simple_message(subject, content, recipients)
    except Exception as ex:
        print(ex.message)
        pass


def get_data(url, apifunc, token, protocol='HTTPS'):

    headers = {"Content-type": "application/json",
               "Authorization": token,
               "HTTP_REFERER": "etools.unicef.org",
               # "Cookie": "tfUDK97TJSCkB4Nlm2wuMx67XNOYWpKT18BeV3RNoeq6nO7FXemAZypct369yF9I",
               # "X-CSRFToken": 'tfUDK97TJSCkB4Nlm2wuMx67XNOYWpKT18BeV3RNoeq6nO7FXemAZypct369yF9I',
               # "username": "achamseddine@unicef.org", "password": "Alouche21!"
               }

    if protocol == 'HTTPS':
        conn = httplib.HTTPSConnection(url)
    else:
        conn = httplib.HTTPConnection(url)
    conn.request('GET', apifunc, "", headers)
    response = conn.getresponse()
    result = response.read()

    if not response.status == 200:
        if response.status == 400 or response.status == 403:
            raise Exception(str(response.status) + response.reason + response.read())
        else:
            raise Exception(str(response.status) + response.reason)

    conn.close()

    return result
