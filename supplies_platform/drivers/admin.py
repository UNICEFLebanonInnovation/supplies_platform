from django.contrib import admin
from .models import Driver, VehicleType
from supplies_platform.users.util import has_group


# Register your models here.


class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'transporter',
        'driver_name',
        'phone_number',
        'vehicle_type',
        'plate_number',)
    fields = (
        'driver_name',
        'phone_number',
        'vehicle_type',
        'plate_number',)

    exclude = ('transporter',)

    # prepopulated_fields = { 'slug' : ['transporter'] }

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
