from __future__ import absolute_import, unicode_literals

import datetime
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from supplies_platform.users.models import Section
from supplies_platform.planning.models import (
    SupplyPlan,
    DistributionPlan,
    DistributionPlanItem,
)


class IndexView(LoginRequiredMixin,
                GroupRequiredMixin,
                TemplateView):

    template_name = 'dashboard/index.html'

    group_required = [u"ADMIN"]

    def get_context_data(self, **kwargs):
        selected_section = int(self.request.GET.get('section', 0))
        plannings = SupplyPlan.objects.filter(plan__isnull=True)
        distributions = DistributionPlan.objects.all()
        requests = DistributionPlanItem.objects.all().order_by('-modified')
        if selected_section:
            plannings = plannings.filter(section_id=selected_section)
            distributions = distributions.filter(plan__section_id=selected_section)
            requests = requests.filter(plan__plan__section_id=selected_section)
        sections = Section.objects.all()

        return {
            'sections': sections,
            'plans': plannings,
            'request_waves': requests,
            'selected_section': selected_section,
            'nbr_planned': plannings.filter(status='submitted').count(),
            'nbr_dist_planned': distributions.filter(status='submitted').count(),
            'nbr_dist_ready': distributions.filter(to_delivery=True, item_received=False).count(),
            # 'nbr_delayed_delivery': requests.filter(plan__approved=True, date_required_by__gte=datetime.datetime.now()).count(),
            # 'nbr_dist_approved': distributions.filter(approved=True, delivery_expected_date__isnull=True).count(),
            # 'nbr_not_received': distributions.filter(delivery_expected_date__gte=datetime.datetime.now(), item_received=False).count()
        }
