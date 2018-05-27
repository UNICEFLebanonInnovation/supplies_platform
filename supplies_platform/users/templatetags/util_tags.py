import json
from django import template
from django.utils.safestring import mark_safe
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from django.core.urlresolvers import resolve
import datetime

register = template.Library()


@register.assignment_tag
def get_range(start, end):
    return (str(x) for x in range(start, end))


@register.assignment_tag
def get_range_int(start, end):
    return (x for x in range(start, end))


@register.assignment_tag
def get_range_str(start, end):
    return (str(x-1)+'/'+str(x) for x in range(start, end))


@register.assignment_tag
def get_range_years(start=1990, end=2051):
    return (str(x) for x in range(start, end))


@register.assignment_tag
def get_range_months(start=1, end=13):
    return (str(x) for x in range(start, end))


@register.assignment_tag
def get_range_days(start=1, end=31):
    return (str(x) for x in range(start, end))


@register.filter
def json_loads(data):
    return json.loads(data)


@register.assignment_tag
def json_load_value(data, key):
    key = key.replace("column", "field")
    list = json.loads(data)
    if key in list:
        return list[key]
    return ''


@register.assignment_tag
def get_user_token(user_id):
    # token = Token.objects.get_or_create(user_id=user_id)
    try:
        token = Token.objects.get(user_id=user_id)
    except Token.DoesNotExist:
        token = Token.objects.create(user_id=user_id)
    return token.key


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        return True if user and group in user.groups.all() else False
    except Group.DoesNotExist:
        return False


@register.filter(name='multiply')
def multiply(value, arg):
    return value*arg


@register.filter(name='percentage')
def percentage(number, total):
    if number:
        return round((number*100.0)/total, 2)
    return 0


@register.assignment_tag
def get_users(group):
    from supplies_platform.users.models import User
    return User.objects.filter(groups__name=group)


@register.assignment_tag
def user_notifications(user):
    from supplies_platform.backends.models import Notification
    print([a.name for a in user.groups.all()])
    notifications = Notification.objects.filter(
        user_group__in=[a.name for a in user.groups.all()]
    ).order_by('-created')
    return notifications


@register.assignment_tag
def user_feeds(user):
    from django.contrib.admin.models import LogEntry
    feeds = LogEntry.objects.exclude(
        content_type__model__in=['user', 'groups', 'group', 'section',
                                 'location', 'location type']).order_by('-action_time')[0:100]
    return feeds
