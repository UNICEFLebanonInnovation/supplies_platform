
from django.contrib import admin
from django.forms import ModelForm

from fsm_admin.mixins import FSMTransitionMixin
from suit.widgets import EnclosedInput

from supplies_platform.users.util import has_group
from .models import ReleaseOrder, LineItem, Section, Driver, VehicleType

#############-----ACTIONS-----########################
def onGoing_tasks(modeladmin, request, queryset):
    queryset.update(status='ONGOING')


onGoing_tasks.short_description = 'Mark as On Going'


def delivered_tasks(modeladmin, request, queryset):
    queryset.update(status='DELIVERED')


delivered_tasks.short_description = 'Mark as Delivered'


#############-----MODEL-ADMINS-----####################
class ItemsAdmin(admin.ModelAdmin):
    list_display = (
        'get_transport',
        'item_code',
        'sales_order_no',
        'po_no',
        'item_desc',
        'unit',
        'dispatch_quantity',
    )

    def get_transport(self, obj):
        return obj.release_order.id

    get_transport.short_description = 'Transport'
    list_filter = ('release_order',)

    def get_readonly_fields(self, request, obj):
        if has_group(request.user, "Transporter"):
            return (
                'release_order',
                'item_code',
                'sales_order_no',
                'po_no',
                'item_desc',
                'unit',
                'dispatch_quantity',
            )


class TransportForm(ModelForm):
    class Meta:
        widgets = {
            'volume': EnclosedInput(append='m<sup>3</sup>'),
        }


class ReleaseOrderAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = (
        'release_order',
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
    )

    form = TransportForm
    fieldsets = (
        ('States', {
            'fields': ('transport_state', 'driver_select_state',)
        }),
        ('Release Order/Waybill', {
            'fields': (
                'release_order',
                'waybill_ref',
                'loading_warehouse',
                'destination_warehouse',
                'delivery_date',
                'transporter',
                'cosignee',
                'focal_point',
                'section',
                'volume',
        )}),
        ('Loading Vehicles at Source Warehouse', {
            'fields': (
                'proposed_loading_time',
                'loading_time_start',
                'loading_time_end',
                'leaving_time',
                'waybill_doc_signed1',
        )}),
        ('Unloading Vehicles at Destination Warehouse', {
            'fields': (
                'unloading_date',
                'unloading_time_start',
                'unloading_time_end',
                'waybill_doc_signed2',
        )}),
        ('Vehicle Information', {
            'fields': ('driver', 'volume',)
        }),
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

        if has_group(request.user, "Unicef"):
            self.fieldsets = (
                ('States', {'fields': ('transport_state', 'driver_select_state',)}),
                ('Release Order/Waybill', {'fields': (
                'release_order', 'waybill_ref', 'loading_warehouse', 'destination_warehouse', 'delivery_date',
                'transporter', 'cosignee', 'focal_point', 'section', 'volume')}),
                ('Loading Vehicles at Source Warehouse',
                 {'fields': ('proposed_loading_time', 'loading_time_start', 'loading_time_end', 'leaving_time',
                             'waybill_doc_signed1',)}),
                ('Unloading Vehicles at Destination Warehouse',
                 {'fields': ('unloading_date', 'unloading_time_start', 'unloading_time_end', 'waybill_doc_signed2',)}),
                ('Vehicle Information', {'fields': ('driver',)}),
            )

        if has_group(request.user, "Warehouse"):
            self.fieldsets = (
                ('States', {'fields': ('transport_state', 'driver_select_state',)}),
                ('Loading Vehicles at Source Warehouse',
                 {'fields': ('proposed_loading_time', 'loading_time_start', 'loading_time_end', 'leaving_time',
                             'waybill_doc_signed1',)}),
                ('Vehicle Information', {'fields': ('driver',)}),
                ('Release Order/Waybill', {'fields': (
                'release_order', 'waybill_ref', 'loading_warehouse', 'destination_warehouse', 'delivery_date',
                'transporter', 'cosignee', 'focal_point', 'section', 'volume',)}),

            )
        if has_group(request.user, "Transporter"):
            self.fieldsets = (
                ('States', {'fields': ('transport_state', 'driver_select_state',)}),
                ('Vehicle Information', {'fields': ('driver',)}),
                ('Loading Vehicles at Source Warehouse',
                 {'fields': ('proposed_loading_time', 'loading_time_start', 'loading_time_end', 'leaving_time',
                             'waybill_doc_signed1',)}),
                ('Unloading Vehicles at Destination Warehouse',
                 {'fields': ('unloading_date', 'unloading_time_start', 'unloading_time_end', 'waybill_doc_signed2',)}),
                ('Release Order/Waybill', {'fields': (
                'release_order', 'waybill_ref', 'loading_warehouse', 'destination_warehouse', 'delivery_date',
                'transporter', 'cosignee', 'focal_point', 'section', 'volume',)}),

            )
        return self.fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            'transport_state',
            'driver_select_state',
        ]
        common_readonly = [
            'release_order',
            'waybill_ref',
            'loading_warehouse',
            'destination_warehouse',
            'delivery_date',
            'transporter',
            'cosignee',
            'focal_point',
            'section',
        ]
        transporter_readonly = [
            'proposed_loading_time',
            'loading_time_start',
            'loading_time_end',
            'leaving_time',
            'waybill_doc_signed1',
        ]
        warehouse_readonly = [
            'unloading_date',
            'unloading_time_start',
            'unloading_time_end',
            'waybill_doc_signed2',
            'driver',
            'volume',
        ]
        unicef_readonly = [
            'unloading_date',
            'unloading_time_start',
            'unloading_time_end',
            'waybill_doc_signed2',
            'driver',
            'loading_time_start',
            'loading_time_end',
            'leaving_time',
            'waybill_doc_signed1'
        ]

        if has_group(request.user, "Warehouse"):
            readonly_fields += common_readonly + warehouse_readonly
        if has_group(request.user, "Transporter"):
            readonly_fields += common_readonly + transporter_readonly
        if has_group(request.user, "Unicef"):
            readonly_fields += unicef_readonly
        return readonly_fields


class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'transporter',
        'driver_name',
        'phone_number',
        'v_type',
        'plate_number',)
    fields = (
        'driver_name',
        'phone_number',
        'v_type',
        'plate_number',)

    exclude = ('transporter',)

    def get_queryset(self, request):
        qs = super(DriverAdmin, self).get_queryset(request)
        if has_group(request.user, "Transporter"):
            return qs.filter(transporter=request.user)
        return qs

    def save_form(self, request, form, change):
        obj = super(DriverAdmin, self).save_form(request, form, change)
        if not change:
            obj.transporter = request.user
        return obj

    def get_readonly_fields(self, request, obj=None):
        readonly = super(DriverAdmin, self).get_readonly_fields(request, obj)
        if has_group(request.user, "Transporter"):
            readonly = ("transporter",)
        return readonly


admin.site.register(Driver, DriverAdmin)
admin.site.register(VehicleType)
admin.site.register(ReleaseOrder, ReleaseOrderAdmin)
admin.site.register(LineItem, ItemsAdmin)
admin.site.register(Section)
# Register your models here.
