from django.contrib import admin

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import SupplyItem, SupplyService, Grant


class SupplyItemResource(resources.ModelResource):
    class Meta:
        model = SupplyItem
        fields = (
            'id',
            'code',
            'description',
            'price',
        )
        export_order = fields


class SupplyItemAdmin(ImportExportModelAdmin):
    resource_class = SupplyItemResource

    fields = (
        'code',
        'description',
        'unit_of_measure',
        'unit_weight',
        'unit_volume',
        'quantity_in_stock',
        'price',
        'stock_value',
        'section',
    )

    search_fields = (
        'code',
        'description',
    )
    list_display = (
        'code',
        'description',
        'quantity_in_stock',
        'price',
        'section',
    )
    list_filter = (
        'section',
    )
    readonly_fields = (
        'stock_value',
    )


class SupplyServiceResource(resources.ModelResource):
    class Meta:
        model = SupplyService
        fields = (
            'id',
            'code',
            'description',
        )
        export_order = fields


class SupplyServiceAdmin(ImportExportModelAdmin):
    resource_class = SupplyServiceResource

    fields = (
        'code',
        'description',
    )

    search_fields = (
        'code',
        'description',
    )
    list_display = (
        'code',
        'description',
    )


admin.site.register(SupplyItem, SupplyItemAdmin)
admin.site.register(SupplyService, SupplyServiceAdmin)
admin.site.register(Grant)
