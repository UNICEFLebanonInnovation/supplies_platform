from django.contrib import admin
from .models import ReleaseOrder, TransportDetail, Item, Warehouse, Section
from supplies_platform.users.util import has_group
from django.core import urlresolvers
from django.db import models
from supplies_platform.drivers.models import Driver


#############-----ACTIONS-----########################

def onGoing_tasks(modeladmin, request, queryset):
    queryset.update(status='ONGOING')


onGoing_tasks.short_description = 'Mark as On Going'


def delivered_tasks(modeladmin, request, queryset):
    queryset.update(status='DELIVERED')


delivered_tasks.short_description = 'Mark as Delivered'


#############-----MODEL-ADMINS-----####################


class ItemsAdmin(admin.ModelAdmin):
    list_display = ('get_transport',
                    'item_code',
                    'sales_order_no',
                    'po_no',
                    'item_desc',
                    'unit',
                    'dispatch_quantity',)

    def get_transport(self, obj):
        return obj.transport_id.id;

    get_transport.short_description = 'Transport'
    list_filter = ('transport_id',)

    def get_readonly_fields(self, request, obj):
       if has_group(request.user,"Transporter"):
          return ('transport_id',
                  'item_code',
                  'sales_order_no',
                  'po_no',
                  'item_desc',
                  'unit',
                  'dispatch_quantity',)



class TransportAdmin(admin.ModelAdmin):
    list_display = (
        'get_parent_waybill',
        'status',
        'driver',
        'proposed_loading_time',
        'loading_time_start',
        'loading_time_end',
        'unloading_time_start',
        'unloading_time_end',
        'delivery_date',
        'total_items',
        'view_link', )

    exclude = ("loading_time",)

    list_filter = ('release_order',)

    # actions = [onGoing_tasks, delivered_tasks]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "driver":
            if has_group(request.user,"Transporter"):
                kwargs["queryset"] = Driver.objects.filter(transporter=request.user)
        return super(TransportAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


    def view_link(self, obj):
        index = obj.id

        change_url = urlresolvers.reverse('admin:transport_item_changelist')
        link = '<a href="' + change_url + '?transport_id=' + str(index) + '">View Items</a>'
        return link

    view_link.short_description = ''
    view_link.allow_tags = True


    # def get_queryset(self, request):
    #     qs = super(TransportAdmin, self).get_queryset(request)
    #     if has_group(request.user,"Transporter"):
    #         qs.filter(transporter=request.user.username)
    #     return qs

    def get_readonly_fields(self, request, obj):
       readonly = super(TransportAdmin, self).get_readonly_fields(request,obj)

       if has_group(request.user,"Transporter"):
          return ('release_order',
                  'status',
                  'proposed_loading_time',
                  'loading_time_start',
                  'delivery_date',
                  'unloading_time',
                  'cosignee',
                  'waybill_signed')
       return readonly

    def get_parent_waybill(self, obj):
        return obj.release_order.waybill_ref
    get_parent_waybill.short_description = 'Parent Waybill'


    def get_queryset(self, request):
        qs = super(TransportAdmin, self).get_queryset(request)
        qs = qs.annotate(models.Count('item'))
        if has_group(request.user,"Transporter"):
            return qs.filter(transporter = request.user)
        return qs

    def total_items(self, obj):
        return obj.item__count
    total_items.admin_order_field = 'item__count'


class TransportInline(admin.StackedInline):
    model = TransportDetail
    extra = 1
    #readonly_fields = ['driver_id',]
    exclude = ['driver_id',
               'delivery_date',
               'loading_time',
               'unloading_time']


class ReleaseOrderAdmin(admin.ModelAdmin):
    inlines = [TransportInline, ]

    list_display = ('release_order',
                    'waybill_ref',
                    'reference_number',
                    'get_loading_warehouse',
                    'get_destination_warehouse',
                    'transporter',
                    'cosignee',
                    'focal_point',
                    'get_section',
                    'total_transport',
                    'view_link')


    def get_queryset(self, request):
        qs = super(ReleaseOrderAdmin, self).get_queryset(request)
        qs = qs.annotate(models.Count('transportdetail'))
        return qs

    def get_loading_warehouse(self, obj):
        return obj.loading_warehouse.name
    get_loading_warehouse.short_description = 'Loading Warehouse'

    def get_destination_warehouse(self, obj):
        return obj.destination_warehouse.name
    get_destination_warehouse.short_description = 'Destination Warehouse'

    def get_section(self, obj):
        return obj.section.name
    get_section.short_description = 'Section'



    def total_transport(self, obj):
        return obj.transportdetail__count
    total_transport.admin_order_field = 'transportdetail__count'

    def view_link(self, obj):
        index = obj.id
        change_url = urlresolvers.reverse('admin:transport_transportdetail_changelist')
        link = '<a href="' + change_url + '?release_order=' + str(index) + '">View Transport</a>'
        return link
    view_link.short_description = ''
    view_link.allow_tags = True


admin.site.register(TransportDetail, TransportAdmin)
admin.site.register(ReleaseOrder, ReleaseOrderAdmin)
admin.site.register(Item, ItemsAdmin)
admin.site.register(Section)
admin.site.register(Warehouse)

# Register your models here.
