# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import time
import datetime

from django.http import HttpResponseForbidden, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from django_filters.views import FilterView
from django_tables2 import RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from .models import SMVisit, AssessmentHash
from .filters import SMVisitFilter
from .tables import BootstrapTable, SMVisitTable, TPMVisitTable
from .serializers import SMVisitSerializer
from supplies_platform.users.util import has_group


class SMListView(LoginRequiredMixin,
                 FilterView,
                 ExportMixin,
                 SingleTableView,
                 RequestConfig):

    table_class = SMVisitTable
    model = SMVisit
    template_name = 'tpm/unicef.visit.html'
    table = BootstrapTable(SMVisit.objects.all(), order_by='-id')

    filterset_class = SMVisitFilter

    def get_queryset(self):
        return SMVisit.objects.filter(type='quality')


class TPMListView(LoginRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):

    table_class = TPMVisitTable
    model = SMVisit
    template_name = 'tpm/tpm.visit.html'
    table = BootstrapTable(SMVisit.objects.all(), order_by='-id')

    filterset_class = SMVisitFilter

    def get_queryset(self):
        if has_group(self.request.user, 'TPM_COMPANY'):
            return SMVisit.objects.filter(assigned_to=self.request.user, type='quantity')
        return SMVisit.objects.all()


class SMAssessment(SingleObjectMixin, RedirectView):
    model = SMVisit

    def get_redirect_url(self, *args, **kwargs):
        tpm_visit = self.get_object()
        assessment_slug = self.request.GET.get('slug')
        assessment_mode = self.request.GET.get('mode')

        hashing = AssessmentHash.objects.create(
            tpm_visit=tpm_visit.id,
            assessment_slug=assessment_slug,
            user=self.request.user.id,
            timestamp=time.time()
        )
        assessment_form = ''
        callback_url = ''
        if assessment_slug == 'quality':
            callback_url = self.request.META.get('HTTP_REFERER', reverse('tpm:unicef_visits', args={}))
            if assessment_mode == 'online':
                assessment_form = 'https://ee.humanitarianresponse.info/single/::YS8V'  # Online only
            else:
                assessment_form = 'https://ee.humanitarianresponse.info/x/#YS8V'  # Online / Offline
        if assessment_slug == 'quantity':
            callback_url = self.request.META.get('HTTP_REFERER', reverse('tpm:tpm_visits', args={}))
            if assessment_mode == 'online':
                assessment_form = 'https://ee.humanitarianresponse.info/single/::YS8O'  # Online only
            else:
                assessment_form = 'https://ee.humanitarianresponse.info/x/::YS8O'  # Online / Offline

        url = '{form}?d[supply]={supply}&d[partnership]={partnership}&d[supply_item]={supply_item}' \
              '&d[location]={location}&d[quantity]={quantity}&d[distribution_date]={distribution_date}' \
              '&returnURL={callback}'.format(
                form=assessment_form,
                supply=hashing.hashed,
                partnership=tpm_visit.supply_plan.pca,
                supply_item=tpm_visit.supply_item,
                location=tpm_visit.site,
                quantity=tpm_visit.quantity_distributed,
                distribution_date=tpm_visit.distribution_date,
                callback=callback_url
        )
        return url


@method_decorator(csrf_exempt, name='dispatch')
class SMVisitSubmission(SingleObjectMixin, View):
    def post(self, request, *args, **kwargs):
        if 'supply' not in request.body:
            return HttpResponseBadRequest()

        payload = json.loads(request.body.decode('utf-8'))

        hashing = AssessmentHash.objects.get(hashed=payload['supply'])

        tpm_visit = SMVisit.objects.get(id=int(hashing.tpm_visit))
        tpm_visit.assessment_completed = True
        tpm_visit.assessment = payload
        tpm_visit.assessment_completed_date = datetime.datetime.now()

        tpm_visit.save()

        return HttpResponse()


class SMVisitViewSet(mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):

    model = SMVisit
    queryset = SMVisit.objects.all()
    serializer_class = SMVisitSerializer
    permission_classes = (permissions.IsAuthenticated,)
