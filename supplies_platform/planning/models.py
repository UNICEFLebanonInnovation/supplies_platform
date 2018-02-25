from __future__ import unicode_literals

from django.db import models

from model_utils.choices import Choices
from model_utils.models import TimeStampedModel

from supplies_platform.locations.models import Location
from supplies_platform.users.models import User, Section
from supplies_platform.partners.models import PartnerOrganization
from supplies_platform.supplies.models import SupplyItem


class SupplyPlan(models.Model):

    partnership = models.CharField(
        max_length=50,
        null=True, blank=True
    )
    partner = models.ForeignKey(
        PartnerOrganization
    )
    section = models.ForeignKey(Section)

    def __unicode__(self):
        return '{} - {}'.format(self.partnership, self.partner)


class SupplyPlanItem(models.Model):
    """
    Planning fields
    """
    supply_plan = models.ForeignKey(SupplyPlan)
    item = models.ForeignKey(SupplyItem)
    quantity = models.PositiveIntegerField(
        help_text=u'PD Quantity'
    )
    wave_number = models.CharField(
        max_length=2,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    date_required_by = models.DateField(
        null=True, blank=True
    )
    # auto generate
    target_population = models.IntegerField(
        verbose_name=u'Max No. of beneficiaries covered',
        null=True, blank=True
    )

    covered_per_item = models.IntegerField(
        verbose_name=u'Beneficiaries covered per item',
        null=True, blank=True
    )

    def __unicode__(self):
        return u'{}-{}-{}'.format(
            self.supply_plan.__unicode__(),
            self.item,
            self.quantity
        )


class WavePlan(models.Model):

    supply_plan = models.ForeignKey(SupplyPlan)
    supply_item = models.ForeignKey(SupplyItem)
    wave_number = models.CharField(
        max_length=2,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    quantity_required = models.PositiveIntegerField(
        help_text=u'Quantity required for this wave',
        null=True, blank=True
    )
    date_required_by = models.DateField(
        null=True, blank=True
    )

    def __unicode__(self):
        return u'{} Wave: {}'.format(
            self.supply_item.__unicode__(),
            self.wave_number,
        )


class DistributionPlan(models.Model):
    plan = models.ForeignKey(SupplyPlan)


class DistributionPlanItem(models.Model):
    """
    Distribution Fields
    """
    plan = models.ForeignKey(DistributionPlan)
    wave = models.ForeignKey(WavePlan)
    site = models.ForeignKey(Location)
    purpose = models.CharField(
        max_length=50,
        null=True, blank=True,
        choices=Choices(
            ('emergency_request', 'Emergency Request',),
            ('pd_request', 'PD Request',),
        )
    )
    target_population = models.IntegerField(
        verbose_name=u'No. of beneficiaries covered',
        null=True, blank=True
    )
    delivery_location = models.ForeignKey(
        Location,
        null=True, blank=True,
        related_name='supply_items'
    )
    contact_person = models.ForeignKey(
        User,
        null=True, blank=True
    )
    quantity_requested = models.PositiveIntegerField(
        verbose_name=u'Quantity required for this location',
        null=True, blank=True
    )
    date_required_by = models.DateField(
        null=True, blank=True,
    )
    date_distributed_by = models.DateField(
        verbose_name=u'planned distribution date',
        null=True, blank=True
    )
    quantity_received = models.PositiveIntegerField(
        null=True, blank=True
    )
    date_received = models.DateField(
        null=True, blank=True,
    )
    quantity_balance = models.PositiveIntegerField(
        null=True, blank=True
    )
    date_distributed = models.DateField(
        null=True, blank=True,
    )
    quantity_distributed = models.PositiveIntegerField(
        null=True, blank=True
    )

    def __unicode__(self):
        return u'{} Site: {}'.format(
            self.wave.__unicode__(),
            self.site,
        )


class DistributionItemRequest(TimeStampedModel):

    plan = models.ForeignKey(DistributionPlan)
    quantity = models.PositiveIntegerField(
        null=True, blank=True
    )
    expected_date = models.DateField(
        null=True, blank=True
    )
    requested_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    to_review = models.BooleanField(blank=True, default=False)
    review_date = models.DateField(
        null=True, blank=True
    )
    reviewed_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    to_validate = models.BooleanField(blank=True, default=False)
    validation_date = models.DateField(
        null=True, blank=True
    )
    validated_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    to_approve = models.BooleanField(blank=True, default=False)
    approval_date = models.DateField(
        null=True, blank=True
    )
    approved_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    delivery_date = models.DateField(
        null=True, blank=True
    )
    status = models.CharField(max_length=20, null=True, blank=True)

