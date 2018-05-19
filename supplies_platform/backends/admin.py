# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.contrib.admin.models import LogEntry

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import Notification


class NotificationResource(resources.ModelResource):
    class Meta:
        model = Notification
        fields = (
            'name',
            'description',
            'type',
            'status',
            'ticket',
            'school',
            'created',
        )
        export_order = fields


class NotificationAdmin(ImportExportModelAdmin):
    resource_class = NotificationResource
    list_display = (
        'subject',
        'description',
        'user_group',
        'status',
        'created',
    )

    list_filter = (
        'user_group',
        'status',
    )

    search_fields = (
        'subject',
        'description',
    )


admin.site.register(LogEntry)
admin.site.register(Notification, NotificationAdmin)
