from django.contrib import admin
from .models import Driver, VehicleType

# Register your models here.


class DriverAdmin(admin.ModelAdmin):
     list_display = (
        'transporter','driver_name', 'phone_number', 'vehicle_type', 'plate_number',)


admin.site.register(Driver,DriverAdmin)
admin.site.register(VehicleType)

