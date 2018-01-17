from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition

from model_utils.models import TimeStampedModel

from supplies_platform.locations.models import Location
from supplies_platform.planning.models import Section
from supplies_platform.users.models import User
from supplies_platform.users.util import has_group


class TransportState(object):
    '''
    Constants to represent the `state`s of the Warehouse-TRANSPORT Model
    '''
    # STARTED = 'started'
    SET_PROPOSED_LOADING_TIME = 'Proposed Loading Time'
    CONFIRM_LOADING_TIME = 'Confirmed Loading Time'
    SET_ACTUAL_LOADING_TIME = 'Actual Loading Time'
    SET_ACTUAL_LEAVING_TIME = 'Leaving Time'
    SET_UNLOADING_TIME = 'Unloading Time'
    COMPLETED = 'Completed'

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
    REQUEST_DRIVER = 'Set volume'
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


class VehicleType(models.Model):

    type = models.CharField(max_length=256)

    def __str__(self):
        return self.type


class Driver(models.Model):

    v_type = models.ForeignKey(VehicleType)
    transporter= models.ForeignKey(User)
    driver_name = models.CharField(max_length=256)
    phone_number = models.CharField(
        _('Phone number'),
        max_length=20, null=True, blank=True
    )
    plate_number = models.CharField(max_length=256L)


    def __str__(self):
        return self.driver_name +"-"+self.v_type.type+"-"+self.plate_number


class ReleaseOrder(TimeStampedModel):
    # First Name and     Last Name do not cover name patterns
    # around the globe.
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

    release_order = models.CharField(max_length=256)
    waybill_ref = models.CharField(max_length=256)
    section = models.ForeignKey(Section)
    delivery_date = models.DateField(default=now)
    waybill_doc = models.FileField(
        upload_to='documents/',
        null=True, blank=True
    )
    cosignee = models.ForeignKey(
        User, related_name="Cosignee+",
        null=True, blank=True
    )
    focal_point = models.ForeignKey(
        User, related_name="Focal Point+"
    )
    loading_warehouse = models.ForeignKey(
        Location, related_name="loading warehouse+"
    )
    destination_warehouse = models.ForeignKey(
        Location, related_name="destination warehouse+"
    )
    transporter = models.ForeignKey(
        User, related_name="Transporter Company+",
        null=True, blank=True
    )

    #FROM TRANSPORT
    proposed_loading_time = models.TimeField(null=True, blank=True)
    loading_time_start = models.TimeField(null=True, blank=True)
    loading_time_end = models.TimeField(null=True, blank=True)
    unloading_date = models.DateField(null=True, blank=True)
    unloading_time_start = models.TimeField(null=True, blank=True)
    unloading_time_end = models.TimeField(null=True, blank=True)
    leaving_time = models.TimeField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    waybill_doc_signed1 = models.FileField(
        upload_to='documents/', null=True, blank=True
    )
    waybill_doc_signed2 = models.FileField(
        upload_to='documents/', null=True, blank=True
    )
    driver = models.ForeignKey(Driver, null=True, blank=True)

    def __str__(self):
        return self.release_order + " " + self.waybill_ref

    def has_volume_set(self):

        # print "TEST:"+str(self.volume)
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
        return self.loading_time_start and \
               self.loading_time_end  and \
               self.leaving_time and \
               self.waybill_doc_signed1
    has_loading_time_set.hint = 'Set Start and End time for loading.'

    def has_unloading_time_set(self):
        #  print "TEST:"+str(self.volume)
        return self.unloading_time_start and \
               self.unloading_time_end and \
               self.waybill_doc_signed2
    has_unloading_time_set.hint = 'Set Start and End time for unloading.'

    def only_unicef_group(self, user):
        return has_group(user, "Unicef")

    def only_transporter_group(self, user):
        return has_group(user, "Transporter")

    def only_warehouse_group(self, user):
        return has_group(user, "Warehouse")

            ########################################################
    # Workflow (state) Transitions

    @transition(
        field=driver_select_state,
        source=DriverState.REQUEST_DRIVER,
        target=DriverState.SET_DRIVER,
        conditions=[has_volume_set],
        permission=only_unicef_group,
        custom={"button_name": "Send to transporter"})
    def save_and_send_transporter(self):
        """

        :return:
        """

    @transition(
        field=driver_select_state,
        source=DriverState.SET_DRIVER,
        target=DriverState.CONFIRM_DRIVER,
        conditions=[has_driver_set],
        permission=only_transporter_group,
        custom={"button_name": "Set Driver"})
    def set_driver(self):
        """

        :return:
        """

    @transition(
        field=driver_select_state,
        source=DriverState.CONFIRM_DRIVER,
        target=DriverState.COMPLETED,
        conditions=[has_driver_set],
        permission=only_unicef_group,
        custom={"button_name": "Confirm Driver"})
    def confirm_driver(self):
        """

        :return:
        """

    @transition(
        field=transport_state,
        source=TransportState.SET_PROPOSED_LOADING_TIME,
        target=TransportState.CONFIRM_LOADING_TIME,
        conditions=[has_proposed_time],
        permission=only_unicef_group,
        custom={"button_name": "Send Loading Time"})
    def send_loading_time(self):
        """

        :return:
        """

    @transition(
        field=transport_state,
        source=TransportState.CONFIRM_LOADING_TIME,
        target=TransportState.SET_ACTUAL_LOADING_TIME,
        conditions=[has_proposed_time],
        permission=only_warehouse_group,
        custom={"button_name": "Confirm Loading Time"})
    def confirm_loading_time(self):
        """

        :return:
        """

    @transition(
        field=transport_state,
        source=TransportState.SET_ACTUAL_LOADING_TIME,
        target=TransportState.SET_UNLOADING_TIME,
        conditions=[has_loading_time_set],
        permission=only_warehouse_group,
        custom={"button_name": "Set Loading Time"})
    def set_loading_time(self):
        """

        :return:
        """

    @transition(
        field=transport_state,
        source=TransportState.SET_UNLOADING_TIME,
        target=TransportState.COMPLETED,
        conditions=[has_unloading_time_set],
        permission=only_transporter_group,
        custom={"button_name": "Set Unloading Time"})
    def set_unloading_time(self):
        '''
        Publish the object.
        '''


class LineItem(TimeStampedModel):
    """
    # First Name and Last Name do not cover name patterns
    # around the globe.
    # ro_id = models.ForeignKey(ReleaseOrder, on_delete=models.CASCADE)
    """

    release_order = models.ForeignKey(ReleaseOrder)
    item_code = models.CharField(max_length=256)
    sales_order_no = models.IntegerField()
    po_no = models.IntegerField()
    item_desc = models.CharField(max_length=256)
    unit = models.CharField(max_length=256)
    dispatch_quantity = models.IntegerField()

    def __str__(self):
        return self.item_code
