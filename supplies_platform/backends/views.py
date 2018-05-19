# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse

from rest_framework import status
from rest_framework import viewsets, mixins, permissions


from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):

    model = Notification
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
