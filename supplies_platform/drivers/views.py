from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from braces.views import GroupRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from .models import Driver
from supplies_platform.transport.models import TransportDetail

#@group_required('Transporter')
class DriverMainView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   ListView):


    group_required = [u"Transporter"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()


class DriverListView(DriverMainView):
    model = Driver

    def get_context_data(self, **kwargs):
        data = {}

        data['driver_list'] = Driver.objects.filter(transporter__id=self.request.user.id).order_by("driver_name")

        data['transport_list'] = TransportDetail.objects.filter(transporter__id=self.request.user.id).order_by("delivery_date")

        print data['driver_list']

        return data





