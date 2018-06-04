from __future__ import absolute_import, unicode_literals

import datetime
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from supplies_platform.users.models import Section
from supplies_platform.planning.models import (
    SupplyPlan,
    DistributionPlan,
    DistributionPlanWave,
    DistributionPlanItemReceived,
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
        requests = DistributionPlanWave.objects.all().order_by('-modified')
        if selected_section:
            plannings = plannings.filter(section_id=selected_section)
            distributions = distributions.filter(plan__section_id=selected_section)
            requests = requests.filter(plan__plan__section_id=selected_section)
        sections = Section.objects.all()

        quantity_gap = DistributionPlanItemReceived.objects.extra(where=[
            'date_received IS NOT NULL', 'quantity_requested != quantity_received'
        ]).values_list('plan_id', flat=True).distinct()

        quantity_gap_plans = DistributionPlan.objects.filter(pk__in=quantity_gap)

        delayed_delivery_plans = DistributionPlan.objects.filter(
            received__isnull=False,
            received__date_received__isnull=True,
            plan_waves__isnull=False,
            plan_waves__delivery_expected_date__isnull=False,
            plan_waves__delivery_expected_date__lt=datetime.datetime.now()
        ).distinct()

        upcoming_delivery_plan = DistributionPlan.objects.filter(
            received__isnull=False,
            received__date_received__isnull=True,
            plan_waves__isnull=False,
            plan_waves__delivery_expected_date__isnull=False,
            plan_waves__delivery_expected_date__gte=datetime.datetime.now(),
            plan_waves__delivery_expected_date__lte=datetime.datetime.now() + datetime.timedelta(days=15),
        ).distinct()

        return {
            'sections': sections,
            'plans': plannings,
            'request_waves': requests,
            'selected_section': selected_section,
            'nbr_quantity_gap': quantity_gap.count(),
            'quantity_gap_plans': quantity_gap_plans,
            'nbr_delayed_delivery': delayed_delivery_plans.count(),
            'delayed_delivery_plans': delayed_delivery_plans,
            'upcoming_delivery_plan': upcoming_delivery_plan,
            'nbr_upcoming_delivery': upcoming_delivery_plan.count(),
            'nbr_actions_sm': 0,
            'nbr_actions_24h': 0,
            'nbr_stock_not_available': 0,
            'nbr_planned': plannings.filter(status='submitted').count(),
            'nbr_dist_planned': distributions.filter(status='submitted').count(),
        }
