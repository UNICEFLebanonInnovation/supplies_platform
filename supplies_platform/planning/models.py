from __future__ import unicode_literals

from django.db import models

from model_utils.choices import Choices

from supplies_platform.locations.models import Location
from supplies_platform.supplies.models import SupplyItem
from supplies_platform.users.models import User


# Create your models here.
class Section(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class SupplyPlan(models.Model):

    partnership = models.CharField(
        max_length=50,
        null=True, blank=True
    )
    section = models.ForeignKey(Section)

    def __unicode__(self):
        return self.partnership


class SupplyPlanItem(models.Model):
    """
    Planning fields
    """
    supply_plan = models.ForeignKey(SupplyPlan)
    purpose = models.CharField(
        max_length=50,
        null=True, blank=True,
        choices=Choices(
            ('emergency_request', 'Emergency Request',),
            ('pd_request', 'PD Request',),
        )
    )
    item = models.ForeignKey(SupplyItem)
    quantity = models.PositiveIntegerField(
        help_text=u'PD Quantity'
    )
    # auto generate
    target_population = models.IntegerField(
        help_text=u'No. of beneficiaries',
        null=True, blank=True
    )

    covered_per_item = models.IntegerField(
        help_text=u'Beneficiaries covered per item',
        null=True, blank=True
    )

    """
    Distribution Fields
    """
    site = models.ForeignKey(Location, null=True)
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
        help_text=u'Quantity required for this location',
        null=True, blank=True
    )
    date_required_by = models.DateField(
        null=True, blank=True
    )
    date_distributed_by = models.DateField(
        null=True, blank=True
    )

    def __unicode__(self):
        return u'{}-{}-{}'.format(
            self.item,
            self.site,
            self.quantity
        )


class DistributionPlan(SupplyPlan):
    class Meta:
        proxy = True


class DistributionPlanItem(SupplyPlanItem):
    class Meta:
        proxy = True
