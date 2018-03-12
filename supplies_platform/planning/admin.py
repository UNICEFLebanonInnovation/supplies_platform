import datetime

from django.contrib import admin
from django import forms

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from supplies_platform.users.util import has_group
from supplies_platform.supplies.models import SupplyItem
from .models import (
    SupplyPlan,
    WavePlan,
    SupplyPlanItem,
    DistributionPlan,
    DistributionPlanItem
)


class SupplyPlanItemInline(admin.TabularInline):
    model = SupplyPlanItem
    verbose_name = 'Supply Item'
    verbose_name_plural = 'Supply Items'
    suit_classes = u'suit-tab suit-tab-waves'

    fields = (
        'item',
        'quantity',
        'wave_number_1',
        'wave_quantity_1',
        'date_required_by_1',
        'wave_number_2',
        'wave_quantity_2',
        'date_required_by_2',
        'wave_number_3',
        'wave_quantity_3',
        'date_required_by_3',
        'wave_number_4',
        'wave_quantity_4',
        'date_required_by_4',
        'covered_per_item',
        'target_population',
    )
    readonly_fields = (
        'target_population',
        'covered_per_item',
    )


class WavePlanFormSet(forms.BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super(WavePlanFormSet, self).get_form_kwargs(index)
        kwargs['parent_object'] = self.instance
        return kwargs


class WavePlanForm(forms.ModelForm):

    class Meta:
        model = WavePlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Only show supply items already in the supply plan
        """
        if 'parent_object' in kwargs:
            self.parent_object = kwargs.pop('parent_object')

        super(WavePlanForm, self).__init__(*args, **kwargs)

        queryset = SupplyItem.objects.none()
        if hasattr(self, 'parent_object'):

            items = self.parent_object.supplyplanitem_set.all().values_list('item__id', flat=True)
            queryset = SupplyItem.objects.filter(id__in=items)

        self.fields['supply_item'].queryset = queryset


class SupplyPlanWaveInlineAdmin(admin.TabularInline):
    model = WavePlan
    form = WavePlanForm
    formset = WavePlanFormSet
    fields = [u'supply_item', u'wave_number', u'quantity_required', u'date_required_by']

    # def get_max_num(self, request, obj=None, **kwargs):
    #     """
    #     Only show these inlines if we have supply plans
    #     :param request:
    #     :param obj: SupplyPlan object
    #     :param kwargs:
    #     :return:
    #     """
    #     if obj and obj.supplyplanitem_set.count():
    #         return self.max_num
    #     return 0


class SupplyPlanResource(resources.ModelResource):
    class Meta:
        model = SupplyPlan
        fields = (
            'partnership',
            'partner',
            'section',
            'status',
            'created',
            'created_by',
            'approved',
        )
        export_order = fields


class SupplyPlanAdmin(ImportExportModelAdmin):
    resource_class = SupplyPlanResource
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'partnership',
                'partner',
                'section',
                'status',
                'created',
                'created_by',
                'approved',
                'partnership_start_date',
                'partnership_end_date',
                # 'approved_by',
                # 'approval_date',
            ]
        }),
    ]

    suit_form_tabs = (
                      ('general', 'Supply Plan'),
                      ('waves', 'Supply Items'),
                    )

    inlines = [SupplyPlanItemInline, ]

    ordering = (u'-created',)
    date_hierarchy = u'created'
    search_fields = (
        'partner__name',
        'partnership',
    )
    list_display = (
        'partner',
        'partnership',
        'section',
        'status',
        'created',
        'created_by',
        'approval_date',
        'approved_by',
    )
    list_filter = (
        'partner',
        'status',
        'approved',
        'approved_by',
        'approval_date',
        'section',
    )

    def get_readonly_fields(self, request, obj=None):

        fields = [
            'status',
            'created',
            'created_by',
            'approved',
            'approved_by',
            'approval_date',
            'partnership_start_date',
            'partnership_end_date',
        ]

        if has_group(request.user, 'BUDGET_OWNER') and obj and obj.status == obj.PLANNED:
            fields.remove('approved')
            fields.remove('approved_by')
            fields.remove('approval_date')

        if has_group(request.user, 'UNICEF_PA'):
            fields.remove('status')

        return fields

    def get_form(self, request, obj=None, **kwargs):
        form = super(SupplyPlanAdmin, self).get_form(request, obj, **kwargs)
        form.request = request
        user = request.user
        form.base_fields['section'].initial = user.section
        if has_group(request.user, 'BUDGET_OWNER') and 'approved_by' in form.base_fields:
            form.base_fields['approved_by'].initial = user

        return form

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        if obj and obj.approved is True and not obj.approval_date:
            obj.approval_date = datetime.datetime.now()
            obj.approved_by = request.user
            obj.status = obj.APPROVED
            DistributionPlan.objects.create(plan=obj)
        super(SupplyPlanAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(SupplyPlanAdmin, self).get_queryset(request)
        if has_group(request.user, 'UNICEF_PA'):
            qs = qs.filter(created_by=request.user)
        if has_group(request.user, 'BUDGET_OWNER'):
            qs = qs.filter(status__in=['planned', 'approved'])
        return qs


class DistributionPlanItemInline(admin.TabularInline):
    model = DistributionPlanItem
    verbose_name = 'Request'
    verbose_name_plural = 'Requests'

    fields = (
        'purpose',
        'wave',
        'site',
        'target_population',
        'delivery_location',
        'contact_person',
        'quantity_requested',
        'date_required_by',
        'date_distributed_by',
    )


class DistributionItemInline(admin.TabularInline):
    model = DistributionPlanItem
    verbose_name = 'Distribution'
    verbose_name_plural = 'Distribution'

    fields = (
        'wave',
        'quantity_received',
        'date_received',
        'quantity_balance',
        'date_distributed',
        'quantity_distributed'
    )


class DistributionPlanResource(resources.ModelResource):
    class Meta:
        model = DistributionPlan
        fields = (
            'plan',
        )
        export_order = fields


class DistributionPlanAdmin(ImportExportModelAdmin):
    resource_class = DistributionPlanResource
    readonly_fields = (
        'plan',
        'plan_partner',
        'plan_partnership',
        'plan_section',
        # DistributionPlanItemInline
    )

    search_fields = (
        'plan__partnership',
    )
    list_display = (
        'plan_partner',
        'plan_partnership',
        'plan_section',
    )
    list_filter = (
        'plan__partner',
        'plan__section',
    )

    inlines = [DistributionPlanItemInline, DistributionItemInline]


admin.site.register(SupplyPlan, SupplyPlanAdmin)
admin.site.register(DistributionPlan, DistributionPlanAdmin)

