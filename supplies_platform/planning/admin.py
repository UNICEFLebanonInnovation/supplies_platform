from django.contrib import admin

# Register your models here.
from .models import (
    SupplyPlan,
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
        'target_population',
        'covered_per_item',
    )
    readonly_fields = (
        'target_population',
        'covered_per_item',
    )


class SupplyPlanAdmin(admin.ModelAdmin):

    inlines = [SupplyPlanItemInline, ]


class DistributionPlanItemInline(admin.TabularInline):
    model = DistributionPlanItem
    verbose_name = 'Item'
    verbose_name_plural = 'Items'

    fields = (
        'purpose',
        'site',
        'target_population',
        'delivery_location',
        'contact_person',
        'item',
        'quantity',
        'quantity_requested',
        'date_required_by',
        'date_distributed_by',
    )

    readonly_fields = (
        'item',
        'quantity',
    )

    def has_add_permission(self, request):
        return False


class DistributionPlanAdmin(SupplyPlanAdmin):

    inlines = [DistributionPlanItemInline, ]


admin.site.register(SupplyPlan, SupplyPlanAdmin)
admin.site.register(DistributionPlan, DistributionPlanAdmin)

