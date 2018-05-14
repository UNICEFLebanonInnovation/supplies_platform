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

from .models import TPMVisit, AssessmentHash
from .filters import TPMVisitFilter
from .tables import BootstrapTable, TPMVisitTable
from .serializers import TPMVisitSerializer
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
        # if has_group(self.request.user, 'TPM_COMPANY'):
        #     return TPMVisit.objects.filter(assigned_to_tpm=self.request.user)
        return TPMVisit.objects.all()

    # def get_context_data(self, **kwargs):
    #
    #     context = super(TPMListView, self).get_context_data(**kwargs)
    #     table = self.get_table(**self.get_table_kwargs())
    #     context[self.get_context_table_name(table)] = table
    #     return context


class TPMAssessment(SingleObjectMixin, RedirectView):
    model = TPMVisit

    def get_redirect_url(self, *args, **kwargs):
        tpm_visit = self.get_object()
        assessment_slug = self.request.GET.get('slug')

        hashing = AssessmentHash.objects.create(
            tpm_visit=tpm_visit.id,
            assessment_slug=assessment_slug,
            user=self.request.user.id,
            timestamp=time.time()
        )
        assessment_form = ''
        if assessment_slug == 'quality':
            assessment_form = 'https://ee.humanitarianresponse.info/single/::YS8O'
        if assessment_slug == 'quantity':
            assessment_form = 'https://ee.humanitarianresponse.info/single/::YS8V'

        url = '{form}?d[supply]={supply}' \
              '&returnURL={callback}'.format(
                form=assessment_form,
                supply=hashing.hashed,
                callback=self.request.META.get('HTTP_REFERER', reverse('tpm:visits', args={}))
        )
        return url


@method_decorator(csrf_exempt, name='dispatch')
class TPMVisitSubmission(SingleObjectMixin, View):
    def post(self, request, *args, **kwargs):
        if 'supply' not in request.body:
            return HttpResponseBadRequest()

        payload = json.loads(request.body.decode('utf-8'))

        hashing = AssessmentHash.objects.get(hashed=payload['supply'])

        tpm_visit = TPMVisit.objects.get(id=int(hashing.tpm_visit))

        if hashing.assessment_slug == 'quantity':
            tpm_visit.quantity_assessment_completed = True
            tpm_visit.quantity_assessment = payload
            tpm_visit.quantity_assessment_completed_date = datetime.datetime.now()

        if hashing.assessment_slug == 'quality':
            tpm_visit.quality_assessment_completed = True
            tpm_visit.quality_assessment = payload
            tpm_visit.quality_assessment_completed_date = datetime.datetime.now()

        tpm_visit.save()

        return HttpResponse()


class TPMVisitViewSet(mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = TPMVisit
    queryset = TPMVisit.objects.all()
    serializer_class = TPMVisitSerializer
    permission_classes = (permissions.IsAuthenticated,)
