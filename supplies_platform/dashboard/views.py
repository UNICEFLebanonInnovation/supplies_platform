from __future__ import absolute_import, unicode_literals

import datetime
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.contrib.admin.models import LogEntry
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from supplies_platform.planning.models import SupplyPlan, DistributionPlan
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
            # user_group__in=['SUPPLY_ADMIN',]
        ).order_by('-created')
        plannings = SupplyPlan.objects.all()
        distributions = DistributionPlan.objects.all()
        return {
            'plans': plannings,
            'feeds': feeds,
            'notifications': notifications[0:20],
            'unread_messages': notifications.filter(status=False).count(),
            'nbr_planned': plannings.filter(status='submitted').count(),
            'nbr_dist_planned': distributions.filter(status='submitted').count(),
            'nbr_dist_ready': distributions.filter(to_delivery=True, item_received=False).count(),
            'nbr_late_dist': distributions.filter(delivery_expected_date__gte=datetime.datetime.now(), item_received=False).count()
        }
