from __future__ import absolute_import, unicode_literals

import datetime
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from supplies_platform.planning.models import SupplyPlan, DistributionPlan, DistributionPlanItem


class IndexView(LoginRequiredMixin,
                GroupRequiredMixin,
                TemplateView):

    template_name = 'dashboard/index.html'

    group_required = [u"ADMIN"]

    def get_context_data(self, **kwargs):
        plannings = SupplyPlan.objects.all()
        distributions = DistributionPlan.objects.all()
        requests = DistributionPlanItem.objects.all()
        return {
            'plans': plannings,
            'nbr_planned': plannings.filter(status='submitted').count(),
            'nbr_dist_planned': distributions.filter(status='submitted').count(),
            'nbr_dist_ready': distributions.filter(to_delivery=True, item_received=False).count(),
            'nbr_delayed_delivery': requests.filter(plan__approved=True, date_required_by__gte=datetime.datetime.now()).count(),
            'nbr_dist_approved': distributions.filter(approved=True, delivery_expected_date__isnull=True).count(),
            'nbr_not_received': distributions.filter(delivery_expected_date__gte=datetime.datetime.now(), item_received=False).count()
        }
