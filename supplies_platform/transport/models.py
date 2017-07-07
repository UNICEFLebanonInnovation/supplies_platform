from __future__ import unicode_literals

from model_utils import Choices
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
from supplies_platform.locations.models import Location
from supplies_platform.drivers.models import Driver
from supplies_platform.users.models import User
from django.utils.timezone import now

from django.db import models


# Create your models here.



#@python_2_unicode_compatible


class Warehouse(models.Model):
    WAREHOUSE_TYPE = Choices(
        ('UNICEF_WH', 'Unicef Warehouse'),
        ('PARTNER_WH', 'Partner Warehouse')
    )

    name = models.CharField(max_length=256L)
    location = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
    )
    type = models.CharField(max_length=256L, choices=WAREHOUSE_TYPE)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=256L)

    def __str__(self):
        return self.name



class ReleaseOrder(TimeStampedModel):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    release_order_id = models.CharField(max_length=256L)
    waybill_ref = models.CharField(max_length=256L)
    reference_number = models.CharField(max_length=256L)
    #waybill_doc_name = models.CharField(max_length=256L)# to change to FileType
    waybill_doc =  models.FileField(upload_to='documents/',null=True,blank=True)

    def __str__(self):
        return  self.release_order_id + " " + self.waybill_ref


class TransportDetail(TimeStampedModel):
    STATUS = Choices(
        ('STARTED', 'Started'),
        ('ONGOING', 'Ongoing'),
        ('DELIVERED', 'Delivered')
    )

    RO_id = models.ForeignKey(ReleaseOrder, on_delete=models.CASCADE)
    sub_waybill_ref = models.CharField(max_length=256L,null=True,blank=True)

    section = models.ForeignKey(Section)
    loading_warehouse = models.ForeignKey(Warehouse,related_name="loading warehouse+")
    destination_warehouse = models.ForeignKey(Warehouse,related_name="destination warehouse+")
    location = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
    )

    cosignee = models.CharField(max_length=256L)
    delivery_date = models.DateField(default=now)
    loading_time = models.TimeField(default=now)
    unloading_time = models.TimeField(default=now)
    status = models.CharField(max_length=256L, choices=STATUS)
    waybill_signed = models.BooleanField()
    focal_point = models.ForeignKey(User,related_name="Focal Point+")
    driver = models.ForeignKey(Driver, null=True, blank=True)
    transporter = models.ForeignKey(User,related_name="Transporter Company+", null=True, blank=True)


    def __str__(self):
        return str(self.id) + " " + str(self.RO_id)



class Item(TimeStampedModel):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    #ro_id = models.ForeignKey(ReleaseOrder, on_delete=models.CASCADE)
    transport_id = models.ForeignKey(TransportDetail)
    item_code = models.CharField(max_length=256L)
    sales_order_no = models.IntegerField()
    po_no = models.IntegerField()
    item_desc = models.CharField(max_length=256L)
    unit = models.CharField(max_length=256L)
    dispatch_quantity = models.IntegerField()


    def __str__(self):
        return self.item_code





