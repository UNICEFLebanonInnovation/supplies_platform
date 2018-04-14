from django.contrib import admin

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import SupplyItem


class SupplyItemResource(resources.ModelResource):
    class Meta:
        model = SupplyItem
        fields = (

        )
        export_order = fields


class SupplyItemAdmin(ImportExportModelAdmin):
    resource_class = SupplyItemResource

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


admin.site.register(SupplyItem, SupplyItemAdmin)
