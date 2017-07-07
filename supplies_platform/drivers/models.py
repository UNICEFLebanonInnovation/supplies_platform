from __future__ import unicode_literals
from supplies_platform.users.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models

# Create your models here.


class VehicleType(models.Model):

    type = models.CharField(max_length=256L)

    def __str__(self):
        return self.type

class Driver(models.Model):

    #transport_id = models.ForeignKey(TransportDetail)
    vehicle_type = models.ForeignKey(VehicleType)
    transporter= models.ForeignKey(User)
    driver_name = models.CharField(max_length=256)
    phone_number = models.CharField(_('Phone number'),max_length=20, null=True, blank=True)
    plate_number = models.CharField(max_length=256L)


    def __str__(self):
        return self.driver_name
