from __future__ import unicode_literals

from model_utils import Choices
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
from supplies_platform.locations.models import Location
from supplies_platform.drivers.models import Driver
from supplies_platform.users.models import User
from django.utils.timezone import now
from django_fsm import FSMField, transition
from supplies_platform.users.util import has_group
from django.core.mail import send_mail

from django.db import models


# Create your models here.



class TransportState(object):
    '''
    Constants to represent the `state`s of the Warehouse-TRANSPORT Model
    '''
    # STARTED = 'started'
    SET_PROPOSED_LOADING_TIME = 'proposed loading time'
    CONFIRM_LOADING_TIME = 'confirmed loading time'
    SET_ACTUAL_LOADING_TIME = 'actual loading time'
    SET_ACTUAL_LEAVING_TIME = 'leaving time'
    SET_UNLOADING_TIME = 'unloading time'
    COMPLETED = 'completed'

    CHOICES = (
        # (STARTED, STARTED),
        (SET_PROPOSED_LOADING_TIME, SET_PROPOSED_LOADING_TIME),
        (CONFIRM_LOADING_TIME, CONFIRM_LOADING_TIME),
        (SET_ACTUAL_LOADING_TIME, SET_ACTUAL_LOADING_TIME),
        (SET_ACTUAL_LEAVING_TIME, SET_ACTUAL_LEAVING_TIME),
        (SET_UNLOADING_TIME, SET_UNLOADING_TIME),
        (COMPLETED, COMPLETED),
    )


class DriverState(object):
    '''
    Constants to represent the `state`s of the Warehouse-TRANSPORT Model
    '''
    # STARTED = 'started'
    REQUEST_DRIVER = 'set volume'
    SET_DRIVER = 'set driver'
    REVISE_VOLUMES = 'revise volumes'
    CONFIRM_DRIVER = 'confirm driver'
    COMPLETED = 'completed'

    CHOICES = (
        (REQUEST_DRIVER, REQUEST_DRIVER),
        (SET_DRIVER, SET_DRIVER),
        (REVISE_VOLUMES, REVISE_VOLUMES),
        (CONFIRM_DRIVER, CONFIRM_DRIVER),
        (COMPLETED, COMPLETED),
    )


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
    warehouse_user = models.ForeignKey(User, related_name="Warehouse Focal Point+", null=True, blank=True)
    warehouse_type = models.CharField(max_length=256L, choices=WAREHOUSE_TYPE)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=256L)

    def __str__(self):
        return self.name


class ReleaseOrder(TimeStampedModel):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    release_order = models.CharField(max_length=256L)
    waybill_ref = models.CharField(max_length=256L)
    reference_number = models.CharField(max_length=256L)
    delivery_date = models.DateField(default=now)
    # waybill_doc_name = models.CharField(max_length=256L)# to change to FileType
    waybill_doc = models.FileField(upload_to='documents/', null=True, blank=True)
    cosignee = models.CharField(max_length=256L, default="")
    focal_point = models.ForeignKey(User, related_name="Focal Point+")
    section = models.ForeignKey(Section)
    loading_warehouse = models.ForeignKey(Warehouse, related_name="loading warehouse+")
    destination_warehouse = models.ForeignKey(Warehouse, related_name="destination warehouse+")
    transporter = models.ForeignKey(User, related_name="Transporter Company+", null=True, blank=True)

    def __str__(self):
        return self.release_order + " " + self.waybill_ref


class TransportDetail(TimeStampedModel):
    # STATUS = Choices(
    #     ('STARTED', 'Started'),
    #     ('ONGOING', 'Ongoing'),
    #     ('DELIVERED', 'Delivered')
    # )

    transport_state = FSMField(
        default=TransportState.SET_PROPOSED_LOADING_TIME,
        verbose_name='Transport State',
        choices=TransportState.CHOICES,
        protected=True,
    )

    driver_select_state = FSMField(
        default=DriverState.REQUEST_DRIVER,
        verbose_name='Driver State',
        choices=DriverState.CHOICES,
        protected=True,
    )

    release_order = models.ForeignKey(ReleaseOrder, on_delete=models.CASCADE)
    proposed_loading_time = models.TimeField(null=True, blank=True)
    loading_time_start = models.TimeField(null=True, blank=True)
    loading_time_end = models.TimeField(null=True, blank=True)
    unloading_time_start = models.TimeField(null=True, blank=True)
    unloading_time_end = models.TimeField(null=True, blank=True)
    leaving_time = models.TimeField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    waybill_doc_signed1 = models.FileField(upload_to='documents/', null=True, blank=True)
    waybill_doc_signed2 = models.FileField(upload_to='documents/', null=True, blank=True)

    # status = models.CharField(max_length=256L, choices=STATUS)
    driver = models.ForeignKey(Driver, null=True, blank=True)

    def __str__(self):
        return str(self.id) + " " + str(self.release_order)



        ########################################################

    # Transition Conditions
    # These must be defined prior to the actual transitions
    # to be refrenced.

    def has_volume_set(self):
        #  print "TEST:"+str(self.volume)
        return self.volume
    has_volume_set.hint = 'Set volume to approximate value.'

    def has_driver_set(self):
        #  print "TEST:"+str(self.volume)
        return self.driver
    has_driver_set.hint = 'Set Driver'

    def has_proposed_time(self):
        #  print "TEST:"+str(self.volume)
        return self.proposed_loading_time
    has_proposed_time.hint = 'Set Proposed Time'

    def has_loading_time_set(self):
        #  print "TEST:"+str(self.volume)
        return self.loading_time_start and self.loading_time_end  and self.leaving_time and self.waybill_doc_signed1
    has_loading_time_set.hint = 'Set Start and End time for loading.'

    def has_unloading_time_set(self):
        #  print "TEST:"+str(self.volume)
        return self.unloading_time_start and self.unloading_time_end and self.waybill_doc_signed2
    has_unloading_time_set.hint = 'Set Start and End time for unloading.'


    def only_unicef_group(self, user):
        if has_group(user, "Unicef"):
            print "TRUE"
            return True
        else:
            return False

    def only_transporter_group(self, user):
        if has_group(user, "Transporter"):
            print "TRUE"
            return True
        else:
            return False

    def only_warehouse_group(self, user):
        if has_group(user, "Warehouse"):
            print "TRUE"
            return True
        else:
            return False

    # def can_display(self):
    #     '''
    #     The display dates must be valid for the current date
    #     '''
    #     return self.check_displayable(timezone.now())
    # can_display.hint = 'The display dates may need to be adjusted.'
    #
    # def is_expired(self):
    #     return self.state == State.EXPIRED
    #
    # def check_displayable(self, date):
    #     '''
    #     Check that the current date falls within this object's display dates,
    #     if set, otherwise default to being displayable.
    #     '''
    #     if not self.has_display_dates():
    #         return True
    #
    #     displayable = self.display_from < date and self.display_until > date
    #     # Expired Pages should transition to the expired state
    #     if not displayable and not self.is_expired:
    #         self.expire()  # Calling the expire transition
    #         self.save()
    #     return displayable

    ########################################################
    # Workflow (state) Transitions

    @transition(field=driver_select_state, source=DriverState.REQUEST_DRIVER,
                target=DriverState.SET_DRIVER,
                conditions=[has_volume_set], permission=only_unicef_group, custom={"button_name":"Save and Send to transporter"})
    def save_and_send_transporter(self):
        self.save()
        '''
        Publish the object.
        '''

    @transition(field=driver_select_state, source=DriverState.SET_DRIVER,
                target=DriverState.CONFIRM_DRIVER,
                conditions=[has_driver_set], permission=only_transporter_group, custom={"button_name":"Set Driver"})
    def set_driver(self):
        '''
        Publish the object.
        '''

    @transition(field=driver_select_state, source=DriverState.CONFIRM_DRIVER,
                target=DriverState.COMPLETED,
                conditions=[has_driver_set], permission=only_unicef_group, custom={"button_name":"Confirm Driver"})
    def confirm_driver(self):
        '''
        Publish the object.
        '''

    @transition(field=transport_state, source=TransportState.SET_PROPOSED_LOADING_TIME,
                target=TransportState.CONFIRM_LOADING_TIME,
                conditions=[has_proposed_time], permission=only_unicef_group, custom={"button_name":"Send Loading Time"})
    def send_loading_time(self):
        '''
        Publish the object.
        '''

    @transition(field=transport_state, source=TransportState.CONFIRM_LOADING_TIME,
                target=TransportState.SET_ACTUAL_LOADING_TIME,
                conditions=[has_proposed_time], permission=only_warehouse_group, custom={"button_name":"Confirm Loading Time"})
    def confirm_loading_time(self):
        '''
        Publish the object.
        '''

    @transition(field=transport_state, source=TransportState.SET_ACTUAL_LOADING_TIME,
                target=TransportState.SET_UNLOADING_TIME,
                conditions=[has_loading_time_set], permission=only_warehouse_group, custom={"button_name":"Set Loading Time"})
    def set_loading_time(self):
        '''
        Publish the object.
        '''

    @transition(field=transport_state, source=TransportState.SET_UNLOADING_TIME,
                target=TransportState.COMPLETED,
                conditions=[has_unloading_time_set], permission=only_transporter_group, custom={"button_name":"Set Unloading Time"})
    def set_unloading_time(self):
        '''
        Publish the object.
        '''



        #
        # @transition(field=state, source=State.PUBLISHED, target=State.EXPIRED,
        #     conditions=[has_display_dates])
        # def expire(self):
        #     '''
        #     Automatically called when a object is detected as being not
        #     displayable. See `check_displayable`
        #     '''
        #     self.display_until = timezone.now()
        #
        # @transition(field=state, source=State.PUBLISHED, target=State.APPROVED)
        # def unpublish(self):
        #     '''
        #     Revert to the approved state
        #     '''
        #
        # @transition(field=state, source=State.DRAFT, target=State.APPROVED)
        # def approve(self):
        #     '''
        #     After reviewed by stakeholders, the Page is approved.
        #     '''


class Item(TimeStampedModel):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    # ro_id = models.ForeignKey(ReleaseOrder, on_delete=models.CASCADE)
    transport_id = models.ForeignKey(TransportDetail)
    item_code = models.CharField(max_length=256L)
    sales_order_no = models.IntegerField()
    po_no = models.IntegerField()
    item_desc = models.CharField(max_length=256L)
    unit = models.CharField(max_length=256L)
    dispatch_quantity = models.IntegerField()

    def __str__(self):
        return self.item_code
