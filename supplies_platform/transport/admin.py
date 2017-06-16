from django.contrib import admin
from .models import ReleaseOrder, TransportDetail, Item, Warehouse, Section
from django.core import urlresolvers
from django.db import models


#############-----ACTIONS-----########################

def onGoing_tasks(modeladmin, request, queryset):
    queryset.update(status='ONGOING')


onGoing_tasks.short_description = 'Mark as On Going'


def delivered_tasks(modeladmin, request, queryset):
    queryset.update(status='DELIVERED')


delivered_tasks.short_description = 'Mark as Delivered'


#############-----MODEL-ADMINS-----####################


class ItemsAdmin(admin.ModelAdmin):
    list_display = ('get_transport', 'item_code', 'sales_order_no', 'po_no', 'item_desc', 'unit',
                    'dispatch_quantity',)

    def get_transport(self, obj):
        return obj.transport_id.id;

    get_transport.short_description = 'Transport'
    list_filter = ('transport_id',)


class TransportAdmin(admin.ModelAdmin):
    list_display = (
        'get_parent_waybill', 'get_section', 'status', 'get_loading_warehouse', 'loading_time', 'delivery_date',
        'get_destination_warehouse', 'total_items', 'view_link')

    list_filter = ('RO_id',)

    # actions = [onGoing_tasks, delivered_tasks]

    def view_link(self, obj):
        index = obj.id

        change_url = urlresolvers.reverse('admin:transport_item_changelist')
        link = '<a href="' + change_url + '?transport_id=' + str(index) + '">View Items</a>'
        return link

    view_link.short_description = ''
    view_link.allow_tags = True

    def get_parent_waybill(self, obj):
        return obj.RO_id.waybill_ref

    get_parent_waybill.short_description = 'Parent Waybill'

    def get_section(self, obj):
        return obj.section.name

    get_section.short_description = 'Section'

    def get_loading_warehouse(self, obj):
        return obj.loading_warehouse.name

    get_loading_warehouse.short_description = 'Loading Warehouse'

    def get_destination_warehouse(self, obj):
        return obj.destination_warehouse.name

    get_destination_warehouse.short_description = 'Destination Warehouse'

    def get_queryset(self, request):
        qs = super(TransportAdmin, self).get_queryset(request)
        qs = qs.annotate(models.Count('item'))
        return qs

    def total_items(self, obj):
        return obj.item__count

    total_items.admin_order_field = 'item__count'


class TransportInline(admin.TabularInline):
    model = TransportDetail
    exclude = ['delivery_date', 'loading_time', 'unloading_time']



class ReleaseOrderAdmin(admin.ModelAdmin):
    inlines = [TransportInline, ]

    list_display = ('release_order_id', 'waybill_ref', 'reference_number', 'total_transport', 'view_link')


    def get_queryset(self, request):
        qs = super(ReleaseOrderAdmin, self).get_queryset(request)
        qs = qs.annotate(models.Count('transportdetail'))
        return qs

    def total_transport(self, obj):
        return obj.transportdetail__count

    total_transport.admin_order_field = 'transportdetail__count'

    def view_link(self, obj):
        index = obj.id

        change_url = urlresolvers.reverse('admin:transport_transportdetail_changelist')
        link = '<a href="' + change_url + '?RO_id=' + str(index) + '">View Transport</a>'
        return link

    view_link.short_description = ''
    view_link.allow_tags = True


admin.site.register(TransportDetail, TransportAdmin)
admin.site.register(ReleaseOrder, ReleaseOrderAdmin)
admin.site.register(Item, ItemsAdmin)
admin.site.register(Section)
admin.site.register(Warehouse)

# Register your models here.
