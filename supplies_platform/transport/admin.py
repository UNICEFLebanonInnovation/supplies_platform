from django.contrib import admin
from .models import ReleaseOrder, Item, Warehouse, Section
from django.forms import ModelForm
from supplies_platform.users.util import has_group
from django.core import urlresolvers
from django.db import models
from supplies_platform.drivers.models import Driver
from fsm_admin.mixins import FSMTransitionMixin
from suit.widgets import EnclosedInput


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
        return obj.release_order.id;

    get_transport.short_description = 'Transport'
    list_filter = ('release_order',)

    def get_readonly_fields(self, request, obj):
        if has_group(request.user, "Transporter"):
            return ('release_order',
                    'item_code',
                    'sales_order_no',
                    'po_no',
                    'item_desc',
                    'unit',
                    'dispatch_quantity',)



# class TransportForm(ModelForm):
#     class Meta:
#         widgets = {
#             'volume': EnclosedInput(append='m<sup>3</sup>'),
#         }
#
#
# class TransportAdmin(FSMTransitionMixin, admin.ModelAdmin):
#     list_display = (
#         'get_parent_waybill',
#         'driver',
#         'proposed_loading_time',
#         'loading_time_start',
#         'loading_time_end',
#         'unloading_time_start',
#         'unloading_time_end',
#         'total_items',
#         'view_link',
#     )
#
#     form = TransportForm
#     fieldsets = (
#         ('States', {'fields': ('transport_state', 'driver_select_state',)}),
#         ('Release Order/Waybill', {'fields': ('release_order',)}),
#         ('Loading Vehicles at Source Warehouse',
#          {'fields': ('proposed_loading_time', 'loading_time_start', 'loading_time_end','leaving_time','waybill_doc_signed1',)}),
#         ('Unloading Vehicles at Destination Warehouse',
#          {'fields': ('unloading_time_start', 'unloading_time_end', 'waybill_doc_signed2',)}),
#         ('Vehicle Information', {'fields': ('driver', 'volume',)}),
#     )
#
#     fsm_field = ('transport_state', 'driver_select_state')
#
#     exclude = ("loading_time",)
#     readonly_fields = ('transport_state', 'driver_select_state')
#     list_filter = ('release_order',)
#
#     #actions = [onGoing_tasks, delivered_tasks]
#
#
#     # def change_view(self, request, object_id, form_url='', extra_context=None):
#     #     extra_context = extra_context or {}
#     #     extra_context['show_save_and_add_another'] = False
#     #     print extra_context
#     #     return super(TransportAdmin, self).change_view(request, object_id,
#     #         form_url, extra_context=extra_context)
#
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "driver":
#             if has_group(request.user, "Transporter"):
#                 kwargs["queryset"] = Driver.objects.filter(transporter=request.user)
#         return super(TransportAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
#     def view_link(self, obj):
#         index = obj.id
#
#         change_url = urlresolvers.reverse('admin:transport_item_changelist')
#         link = '<a href="' + change_url + '?transport_id=' + str(index) + '">View Items</a>'
#         return link
#
#     view_link.short_description = ''
#     view_link.allow_tags = True
#
#     # def get_queryset(self, request):
#     #     qs = super(TransportAdmin, self).get_queryset(request)
#     #     if has_group(request.user,"Transporter"):
#     #         qs.filter(transporter=request.user.username)
#     #     return qs
#
#
#     # def has_add_permission(self, request):
#     #     return False
#
#
#
#     def get_readonly_fields(self, request, obj):
#         readonly = super(TransportAdmin, self).get_readonly_fields(request, obj)
#         if has_group(request.user, "Transporter"):
#             return ('release_order',
#                     'proposed_loading_time',
#                     'transport_state',
#                     'loading_time_start',
#                     'loading_time_end',
#                     'leaving_time'
#                     'volume',
#                     'driver_select_state',)
#
#         elif has_group(request.user, "Warehouse"):
#             return ('release_order',
#                     'proposed_loading_time',
#                     'transport_state',
#                     'volume',
#                     'unloading_time_start',
#                     'unloading_time_end',
#                     'driver_select_state')
#
#         return readonly
#
#     def get_parent_waybill(self, obj):
#         return obj.release_order.waybill_ref
#
#     get_parent_waybill.short_description = 'Parent Waybill'
#
#     def get_queryset(self, request):
#         qs = super(TransportAdmin, self).get_queryset(request)
#         qs = qs.annotate(models.Count('item'))
#         return qs
#
#
#
#     def total_items(self, obj):
#         return obj.item__count
#
#     total_items.admin_order_field = 'item__count'
#
#
# class TransportInline(admin.StackedInline):
#     model = TransportDetail
#     extra = 1
#     # readonly_fields = ['driver_id',]
#     exclude = ['driver',
#                'delivery_date',
#                'loading_time_start',
#                'loading_time_end',
#                'unloading_time_start',
#                'unloading_time_end',
#                'leaving_time',
#                'waybill_doc_signed1',
#                'waybill_doc_signed2',
#                'transport_state',
#                'driver_select_state',
#                ]



class TransportForm(ModelForm):
    class Meta:
        widgets = {
            'volume': EnclosedInput(append='m<sup>3</sup>'),
        }

class ReleaseOrderAdmin(FSMTransitionMixin,admin.ModelAdmin):

    list_display = ('release_order',
                    'waybill_ref',
                    'get_loading_warehouse',
                    'get_destination_warehouse',
                    'delivery_date',
                    'transporter',
                    'cosignee',
                    'focal_point',
                    'get_section',
                    'driver',
                    'proposed_loading_time',
                    'loading_time_start',
                    'loading_time_end',
                    'unloading_time_start',
                    'unloading_time_end',
                    #'total_items',
                    #'total_transport',
                    # 'view_link'
                    )

    form = TransportForm
    fieldsets = (
        ('States', {'fields': ('transport_state', 'driver_select_state',)}),
        ('Release Order/Waybill', {'fields': ('release_order','waybill_ref','loading_warehouse','destination_warehouse','delivery_date','transporter','cosignee','focal_point','section','volume',)}),
        ('Loading Vehicles at Source Warehouse',
         {'fields': ('proposed_loading_time', 'loading_time_start', 'loading_time_end','leaving_time','waybill_doc_signed1',)}),
        ('Unloading Vehicles at Destination Warehouse',
         {'fields': ('unloading_date','unloading_time_start', 'unloading_time_end', 'waybill_doc_signed2',)}),
        ('Vehicle Information', {'fields': ('driver', 'volume',)}),
    )

    fsm_field = ('transport_state', 'driver_select_state')



    def total_items(self, obj):
        return obj.item__count

    total_items.admin_order_field = 'item__count'

    def get_queryset(self, request):
        qs = super(ReleaseOrderAdmin, self).get_queryset(request)
       # qs = qs.annotate(models.Count('transportdetail'))
        if has_group(request.user, "Transporter"):
            return qs.filter(transporter=request.user)
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

    def get_fieldsets(self, request, obj=None):

        if has_group(request.user,"Unicef"):
            self.fieldsets = (
                            ('States', {'fields': ('transport_state', 'driver_select_state',)}),
                            ('Release Order/Waybill', {'fields': ('release_order','waybill_ref','loading_warehouse','destination_warehouse','delivery_date','transporter','cosignee','focal_point','section','volume')}),
                            ('Loading Vehicles at Source Warehouse',
                             {'fields': ('proposed_loading_time', 'loading_time_start', 'loading_time_end','leaving_time','waybill_doc_signed1',)}),
                            ('Unloading Vehicles at Destination Warehouse',
                             {'fields': ('unloading_date','unloading_time_start', 'unloading_time_end', 'waybill_doc_signed2',)}),
                            ('Vehicle Information', {'fields': ('driver',)}),
                            )

        if has_group(request.user,"Warehouse"):
            self.fieldsets = (
                             ('States', {'fields': ('transport_state', 'driver_select_state',)}),
                             ('Loading Vehicles at Source Warehouse',
                             {'fields': ('proposed_loading_time', 'loading_time_start', 'loading_time_end','leaving_time','waybill_doc_signed1',)}),
                             ('Vehicle Information', {'fields': ('driver',)}),
                             ('Release Order/Waybill', {'fields': ('release_order','waybill_ref','loading_warehouse','destination_warehouse','delivery_date','transporter','cosignee','focal_point','section','volume',)}),

    )
        if has_group(request.user,"Transporter"):
            self.fieldsets= (
                            ('States', {'fields': ('transport_state', 'driver_select_state',)}),
                            ('Vehicle Information', {'fields': ('driver',)}),
                            ('Loading Vehicles at Source Warehouse',
                            {'fields': ('proposed_loading_time', 'loading_time_start', 'loading_time_end','leaving_time','waybill_doc_signed1',)}),
                            ('Unloading Vehicles at Destination Warehouse',
                            {'fields': ('unloading_date', 'unloading_time_start', 'unloading_time_end', 'waybill_doc_signed2',)}),
                            ('Release Order/Waybill', {'fields': ('release_order','waybill_ref','loading_warehouse','destination_warehouse','delivery_date','transporter','cosignee','focal_point','section','volume',)}),

    )
        return self.fieldsets


    def get_readonly_fields(self, request, obj=None):
        state_readonly = ('transport_state', 'driver_select_state',)
        common_readonly = ('release_order','waybill_ref','loading_warehouse','destination_warehouse','delivery_date','transporter','cosignee','focal_point','section',)
        transporter_readonly = ('proposed_loading_time', 'loading_time_start', 'loading_time_end','leaving_time','waybill_doc_signed1',)
        warehouse_readonly = ('unloading_date', 'unloading_time_start', 'unloading_time_end', 'waybill_doc_signed2','driver', 'volume',)
        unicef_readonly = ('unloading_date', 'unloading_time_start', 'unloading_time_end', 'waybill_doc_signed2','driver', 'loading_time_start', 'loading_time_end','leaving_time','waybill_doc_signed1')

        if has_group(request.user,"Warehouse"):
            self.readonly_fields = state_readonly + common_readonly + warehouse_readonly
        if has_group(request.user,"Transporter"):
            self.readonly_fields = state_readonly  + common_readonly + transporter_readonly
        if has_group(request.user,"Unicef"):
            self.readonly_fields =  state_readonly + unicef_readonly
        return self.readonly_fields

    # def total_transport(self, obj):
    #     return obj.transportdetail__count

    #total_transport.admin_order_field = 'transportdetail__count'

    # def view_link(self, obj):
    #     index = obj.id
    #     change_url = urlresolvers.reverse('admin:transport_transportdetail_changelist')
    #     link = '<a href="' + change_url + '?release_order=' + str(index) + '">View Transport</a>'
    #     return link
    #
    # view_link.short_description = ''
    # view_link.allow_tags = True


class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse_type', 'warehouse_user',)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "warehouse_user":
    #         kwargs["queryset"] = Warehouse.objects.filter(warehouse_user=)
    #     return super(WarehouseAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


#admin.site.register(TransportDetail, TransportAdmin)
admin.site.register(ReleaseOrder, ReleaseOrderAdmin)
admin.site.register(Item, ItemsAdmin)
admin.site.register(Section)
admin.site.register(Warehouse)

# Register your models here.
