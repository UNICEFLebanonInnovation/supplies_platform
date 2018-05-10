# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from django_filters.views import FilterView
from django_tables2 import RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from .models import TPMVisit
from .filters import TPMVisitFilter
from .tables import BootstrapTable, TPMVisitTable
from supplies_platform.users.util import has_group


class TPMListView(LoginRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):

    table_class = TPMVisitTable
    model = TPMVisit
    template_name = 'tpm/visits.html'
    table = BootstrapTable(TPMVisit.objects.all(), order_by='-id')

    filterset_class = TPMVisitFilter

    def get_queryset(self):
        # if has_group(self.request.user, 'UNICEF_CO'):
        #     return TPMVisit.objects.filter(exported_by=self.request.user)
        # if has_group(self.request.user, 'YOUTH'):
        #     return TPMVisit.objects.filter(partner=self.request.user.partner)

        return TPMVisit.objects.all()
