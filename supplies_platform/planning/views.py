from __future__ import absolute_import, unicode_literals

import datetime
import tablib
from import_export.formats import base_formats
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from supplies_platform.backends.djqscsv import render_to_csv_response

from supplies_platform.users.models import Section
from supplies_platform.supplies.models import SupplyItem, SupplyService
from supplies_platform.planning.models import (
    SupplyPlan,
    SupplyPlanItem,
    SupplyPlanService,
    DistributionPlan,
    DistributionPlanWave,
    DistributionPlanItemReceived,
    SupplyPlanWaveItem,

)


class ExportSupplyGoodsViewSet(ListView):

    model = SupplyPlan
    queryset = SupplyPlan.objects.none()

    def get(self, request, *args, **kwargs):

        data = tablib.Dataset()

        data.headers = [
            'Material No',
            'Material Description',
            'Unit of Measure',
            'Estimated Unit Cost',
            'Required Quantity',

            'Total Estimated Cost',
            'Procuring Entity',
            'Quantity In Stock',
            'Solicitation Method',

            'Grant',
            'Grant Expiry date',
            'Activity ref # in the AWP 2019',
            'Implementing Partner',
            'Prog Focal Point',

            'No of Beneficiaries',

            'Wave 1 Beneficiaries covered',
            'Wave 1 Quantity required',
            'Wave 1 Date goods required by Impl Partner',

            'Wave 2 Beneficiaries covered',
            'Wave 2 Quantity required',
            'Wave 2 Date goods required by Impl Partner',

            'Wave 3 Beneficiaries covered',
            'Wave 3 Quantity required',
            'Wave 3 Date goods required by Impl Partner',

            'Wave 4 Beneficiaries covered',
            'Wave 4 Quantity required',
            'Wave 4 Date goods required by Impl Partner',

            'Comments'
        ]

        qs = SupplyPlanItem.objects.all()

        content = []
        for plan in qs:
            if not plan.plan:
                continue
            item = plan.item

            waves = item.items_distribution_waves.all()
            target_population = 0
            try:
                wave1 = waves[0]
                target_population += wave1.target_population
            except IndexError:
                wave1 = None
            try:
                wave2 = waves[1]
                target_population += wave2.target_population
            except IndexError:
                wave2 = None
            try:
                wave3 = waves[2]
                target_population += wave3.target_population
            except IndexError:
                wave3 = None
            try:
                wave4 = waves[3]
                target_population += wave4.target_population
            except IndexError:
                wave4 = None

            yearly_plan = plan.plan
            yearly_dist_plans = yearly_plan.yearly_dist_plan.all()
            for dist_plan in yearly_dist_plans:
                content = [
                    item.code,
                    item.description,
                    item.unit_of_measure,
                    item.price if item.price else '',
                    plan.quantity,
                    plan.total_budget,
                    'UNICEF',  # Procuring Entity
                    item.quantity_in_stock if item.quantity_in_stock else '',
                    plan.solicitation_method,
                    plan.grant,
                    plan.expiry_date,
                    plan.activity_reference,
                    dist_plan.plan.partner,
                    plan.plan.created_by.name,

                    target_population,

                    wave1.target_population if wave1 else '',
                    wave1.quantity_requested if wave1 else '',
                    wave1.date_distributed_by if wave1 else '',

                    wave2.target_population if wave2 else '',
                    wave2.quantity_requested if wave2 else '',
                    wave2.date_distributed_by if wave2 else '',

                    wave3.target_population if wave3 else '',
                    wave3.quantity_requested if wave3 else '',
                    wave3.date_distributed_by if wave3 else '',

                    wave4.target_population if wave4 else '',
                    wave4.quantity_requested if wave4 else '',
                    wave4.date_distributed_by if wave4 else '',

                    yearly_plan.comments,
                ]
                data.append(content)

        file_format = base_formats.XLSX()
        data = file_format.export_data(data)

        # book = tablib.Databook((data1, data2, data3))

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=SupplyItems.xlsx'
        return response


class ExportSupplyServicesViewSet(ListView):

    model = SupplyPlan
    queryset = SupplyPlan.objects.none()

    def get(self, request, *args, **kwargs):

        data = tablib.Dataset()

        data.headers = [
            'Service Description',
            'Estimated Contract Value',
            'Quantity (if applicable)',

            'Expected Contract Start Date',
            'Expected Contract Duration',
            'Solicitation Method',

            'Grant',
            'Grant Expiry date',
            'Activity ref # in the AWP 2019',
            'Implementing Partner',
            'Programme Focal Point',

            'Comments'
        ]

        qs = SupplyPlanService.objects.all()

        content = []
        for plan in qs:
            item = plan.item

            yearly_plan = plan.plan
            yearly_dist_plans = yearly_plan.yearly_dist_plan.all()
            for dist_plan in yearly_dist_plans:
                content = [
                    item.code,
                    '{}$'.format(plan.expected_amount),
                    plan.quantity,
                    plan.total_budget,
                    '',
                    item.quantity_in_stock if item.quantity_in_stock else '',
                    '',  # Solicitation Method
                    '',  # Grant
                    '',  # Grant Expiry date
                    '',  # Activity ref # in the AWP 2019
                    dist_plan.plan.partner,
                    plan.plan.created_by.name,

                    '',
                ]
                data.append(content)

        file_format = base_formats.XLSX()
        data = file_format.export_data(data)

        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename=supply_services.xlsx'
        return response
