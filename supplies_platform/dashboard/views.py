from __future__ import absolute_import, unicode_literals

import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.contrib.admin.models import LogEntry
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from supplies_platform.planning.models import SupplyPlan
from supplies_platform.backends.models import Notification


class IndexView(LoginRequiredMixin,
                GroupRequiredMixin,
                TemplateView):

    template_name = 'dashboard/index.html'

    group_required = [u"ADMIN"]

    def get_context_data(self, **kwargs):
        feeds = LogEntry.objects.exclude(
            content_type__model__in=['user', 'groups', 'group', 'section',
                                     'location', 'location type']).order_by('-action_time')[0:100]
        notifications = Notification.objects.filter(
            user_group__in=['SUPPLY_ADMIN',]
        ).order_by('-created')[0:20]
        return {
            'plans': SupplyPlan.objects.all(),
            'feeds': feeds,
            'notifications': notifications
            # 'feeds': feeds.order_by('-action_time')
        }
