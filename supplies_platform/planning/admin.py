from django.contrib import admin
from django import forms

# Register your models here.
from .models import (
    SupplyItem,
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

    fields = (
        'item',
        'quantity',
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

    inlines = [SupplyPlanItemInline, SupplyPlanWaveInlineAdmin,]


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
        #'item',
        #'quantity',
        'quantity_requested',
        'date_required_by',
        'date_distributed_by',
    )


    # def has_add_permission(self, request):
    #     return False


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


    # def has_add_permission(self, request):
    #

class DistributionPlanAdmin(SupplyPlanAdmin):

    inlines = [DistributionPlanItemInline, DistributionItemInline]


admin.site.register(SupplyPlan, SupplyPlanAdmin)
admin.site.register(DistributionPlan, DistributionPlanAdmin)

