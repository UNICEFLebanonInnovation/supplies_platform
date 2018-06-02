import datetime

from django.contrib import admin
from django import forms

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from django.contrib.postgres.fields import JSONField
from prettyjson import PrettyJSONWidget


from supplies_platform.users.util import has_group
from .models import (
    SMVisit,
    AssessmentHash
)


class SMVisitResource(resources.ModelResource):
    class Meta:
        model = SMVisit
        fields = (
        )
        export_order = fields


class SMVisitAdmin(ImportExportModelAdmin):
    resource_class = SMVisitResource
    verbose_name = 'SM Visit'
    verbose_name_plural = 'SM Visits'

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'supply_plan_partner',
                'supply_plan_partnership',
                'supply_plan_section',
                'type',
                'site',
                'supply_item',
                'quantity_distributed',
                'distribution_date',
            ]
        }),
        ('Assessment', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'assigned_to',
                'assessment_completed',
                'assessment_completed_date',
                'assessment',
            ]
        })
    ]

    suit_form_tabs = (
                      ('general', 'SM Visit'),
                    )

    readonly_fields = (
        'supply_plan_partner',
        'supply_plan_partnership',
        'supply_plan_section',
        # 'requested_by',
        'site',
        'supply_item',
        'quantity_distributed',
        'distribution_date',
        'assigned_to',
        'assessment_completed',
        'assessment_completed_date',
        'assessment',
    )

    search_fields = (
        'supply_plan__partnership',
    )
    list_display = (
        'supply_plan_partner',
        'supply_plan_partnership',
        'supply_plan_section',
        'type',
        'site',
        'supply_item',
        'quantity_distributed',
        'distribution_date',
        'assessment_completed',
        'assessment_completed_date',
    )
    list_filter = (
        'supply_plan__partner',
        'supply_plan__section',
        'assessment_completed',
        'supply_item',
        'type',
    )

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }

    # def get_readonly_fields(self, request, obj=None):
    #
    #     fields = [
    #
    #     ]
    #
        # if has_group(request.user, 'FIELD_FP') and obj and obj.status == obj.SUBMITTED:
        #     fields.remove('reviewed')
        #     fields.remove('review_comments')
        #
        # if has_group(request.user, 'SUPPLY_FP') and obj and obj.status == obj.REVIEWED:
        #     fields.remove('cleared')
        #     fields.remove('cleared_comments')
        #
        # if has_group(request.user, 'UNICEF_PD') and obj and obj.status == obj.CLEARED:
        #     fields.remove('approved')
        #     fields.remove('approval_comments')
        #
        # if has_group(request.user, 'SUPPLY_FP') and obj and obj.status == obj.APPROVED:
        #     fields.remove('delivery_expected_date')
        #
        # if has_group(request.user, 'PARTNER'):
        #     fields.remove('status')

        # return fields

    def get_queryset(self, request):
        qs = super(SMVisitAdmin, self).get_queryset(request)
        if has_group(request.user, 'TPM_COMPANY'):
            qs = qs.filter(assigned_to=request.user, type='quantity')
        return qs


admin.site.register(SMVisit, SMVisitAdmin)
admin.site.register(AssessmentHash)
