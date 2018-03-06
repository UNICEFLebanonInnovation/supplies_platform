from django.contrib import admin
from django import forms

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


class SupplyPlanAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'partnership',
                'partner',
                'section',
                'approved',
                'approved_by',
                'approval_date'
            ]
        }),
    ]

    suit_form_tabs = (
                      ('general', 'Supply Plan'),
                      ('waves', 'Supply Items'),
                    )

    inlines = [SupplyPlanItemInline,]


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


class DistributionPlanAdmin(admin.ModelAdmin):

    readonly_fields = (
        'plan',
    )

    inlines = [DistributionItemInline, DistributionPlanItemInline]


admin.site.register(SupplyPlan, SupplyPlanAdmin)
admin.site.register(DistributionPlan, DistributionPlanAdmin)

