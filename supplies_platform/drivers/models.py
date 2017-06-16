from __future__ import unicode_literals
from supplies_platform.users.models import User

from django.db import models

# Create your models here.


class VehicleType(models.Model):

    type = models.CharField(max_length=256L)


class Driver(models.Model):

    #transport_id = models.ForeignKey(TransportDetail)
    vehicle_type = models.ForeignKey(VehicleType)
    transporter_company = models.ForeignKey(User)
    plate_number = models.CharField(max_length=256L);
