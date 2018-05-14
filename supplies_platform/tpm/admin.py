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
    TPMVisit,
    AssessmentHash
)


class TPMVisitResource(resources.ModelResource):
    class Meta:
        model = TPMVisit
        fields = (
        )
        export_order = fields


class TPMVisitAdmin(ImportExportModelAdmin):
    resource_class = TPMVisitResource
    verbose_name = 'TPM Visit'
    verbose_name_plural = 'TPM Visits'

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'supply_plan_partner',
                'supply_plan_partnership',
                'supply_plan_section',
                # 'requested_by',
                'site',
                'supply_item',
                'quantity_distributed',
                'distribution_date',
            ]
        }),
        ('Quantity Assessment', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'assigned_to_officer',
                'quantity_assessment_completed',
                'quantity_assessment_completed_date',
                'quantity_assessment',
            ]
        }),
        ('Qualitative Assessment', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'assigned_to_tpm',
                'quality_assessment_completed',
                'quality_assessment_completed_date',
                'quality_assessment',
            ]
        }),
    ]

    suit_form_tabs = (
                      ('general', 'TPM Visit'),
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
        'assigned_to_officer',
        'quantity_assessment_completed',
        'quantity_assessment_completed_date',
        'quantity_assessment',
        'assigned_to_tpm',
        'quality_assessment_completed',
        'quality_assessment_completed_date',
        'quality_assessment',
    )

    search_fields = (
        'supply_plan__partnership',
    )
    list_display = (
        'supply_plan_partner',
        'supply_plan_partnership',
        'supply_plan_section',
        'site',
        'supply_item',
        'quantity_distributed',
        'distribution_date',
        'quantity_assessment_completed',
        'quantity_assessment_completed_date',
        'quality_assessment_completed',
        'quality_assessment_completed_date',
    )
    list_filter = (
        'supply_plan__partner',
        'supply_plan__section',
        'quantity_assessment_completed',
        'quality_assessment_completed',
        'supply_item',
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
        qs = super(TPMVisitAdmin, self).get_queryset(request)
        if has_group(request.user, 'TPM_COMPANY'):
            qs = qs.filter(assigned_to_tpm=request.user)
        return qs


admin.site.register(TPMVisit, TPMVisitAdmin)
admin.site.register(AssessmentHash)
