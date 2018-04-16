from __future__ import unicode_literals

from django.db import models

from model_utils.choices import Choices
from model_utils.models import TimeStampedModel

from django.conf import settings
from smart_selects.db_fields import ChainedForeignKey

from supplies_platform.locations.models import Location
from supplies_platform.users.models import User, Section
from supplies_platform.partners.models import PartnerOrganization, PartnerStaffMember, PCA
from supplies_platform.supplies.models import SupplyItem


class SupplyPlan(TimeStampedModel):

    DRAFT = u'draft'
    PLANNED = u'planned'
    SUBMITTED = u'submitted'
    REVIEWED = u'reviewed'
    APPROVED = u'approved'
    COMPLETED = u'completed'
    CANCELLED = u'cancelled'
    STATUS = (
        (DRAFT, u"Draft"),
        (PLANNED, u"Planned"),
        (SUBMITTED, u"Submitted"),
        (REVIEWED, u"Reviewed"),
        (APPROVED, u"Approved"),
        (COMPLETED, u"Completed"),
        (CANCELLED, u"Cancelled"),
    )

    partnership = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=''
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        null=True, blank=False,
        verbose_name='Partner Organization'
    )
    pca = ChainedForeignKey(
        PCA,
        chained_field="partner",
        chained_model_field="partner",
        show_all=False,
        auto_choose=False,
        null=True, blank=True,
        verbose_name='Partnership/Reference Number',
    )
    section = models.ForeignKey(
        Section,
        null=True, blank=False
    )
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=DRAFT,
    )
    to_review = models.BooleanField(blank=True, default=False)
    reviewed = models.BooleanField(blank=True, default=False)
    review_date = models.DateField(
        null=True, blank=True
    )
    reviewed_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    review_comments = models.TextField(
        null=True, blank=True,
    )
    to_approve = models.BooleanField(blank=True, default=False)
    approved = models.BooleanField(blank=True, default=False)
    approval_date = models.DateField(
        null=True, blank=True
    )
    approved_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    approval_comments = models.TextField(
        null=True, blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
        verbose_name='Planned by'
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='modifications',
        verbose_name='Modified by',
    )
    comments = models.TextField(
        null=True, blank=True,
    )

    @property
    def total_budget(self):
        total = 0.0
        try:
            items = self.supply_plans.all()
            for item in items:
                total += item.quantity * item.item.price
        except Exception as ex:
            pass
        return '{} {}'.format(
            total,
            '$'
        )

    def __unicode__(self):
        return '{} - {}'.format(self.partnership, self.partner)


class SupplyPlanItem(models.Model):
    """
    Planning fields
    """
    supply_plan = models.ForeignKey(SupplyPlan, related_name='supply_plans')
    item = models.ForeignKey(SupplyItem)
    quantity = models.PositiveIntegerField(
        help_text=u'PD Quantity'
    )

    wave_number_1 = models.CharField(
        max_length=2,
        null=True, blank=False,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    wave_quantity_1 = models.PositiveIntegerField(
        null=True, blank=False
    )
    date_required_by_1 = models.DateField(
        null=True, blank=False
    )

    wave_number_2 = models.CharField(
        max_length=2,
        null=True, blank=True,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    wave_quantity_2 = models.PositiveIntegerField(
        null=True, blank=True
    )
    date_required_by_2 = models.DateField(
        null=True, blank=True
    )

    wave_number_3 = models.CharField(
        max_length=2,
        null=True, blank=True,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    wave_quantity_3 = models.PositiveIntegerField(
        null=True, blank=True
    )
    date_required_by_3 = models.DateField(
        null=True, blank=True
    )

    wave_number_4 = models.CharField(
        max_length=2,
        null=True, blank=True,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    wave_quantity_4 = models.PositiveIntegerField(
        null=True, blank=True
    )
    date_required_by_4 = models.DateField(
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

    @property
    def item_price(self):
        if self.item:
            return '{} {}'.format(
                self.item.price,
                '$'
            )
        return ''

    @property
    def total_budget(self):
        total = 0.0
        try:
            total = self.quantity * self.item.price
        except Exception as ex:
            pass
        return '{} {}'.format(
            total,
            '$'
        )

    def __unicode__(self):
        return u'{}-{}-{}'.format(
            self.supply_plan.__unicode__(),
            self.item,
            self.quantity
        )


class WavePlan(models.Model):

    supply_plan = models.ForeignKey(SupplyPlanItem, related_name='supply_plans_waves')
    # supply_item = models.ForeignKey(SupplyItem)
    # supply_plan_item = models.ForeignKey(SupplyPlanItem)
    wave_number = models.CharField(
        max_length=2,
        null=True, blank=False,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    quantity_required = models.PositiveIntegerField(
        help_text=u'Quantity required for this wave',
        null=True, blank=False
    )
    date_required_by = models.DateField(
        null=True, blank=False
    )

    def __unicode__(self):
        return u'Wave {}: Item: {}/{} - Quantity: {}'.format(
            self.wave_number,
            self.supply_plan.item.code,
            self.supply_plan.item.description,
            self.quantity_required,
        )


class DistributionPlan(models.Model):

    DRAFT = u'draft'
    PLANNED = u'planned'
    SUBMITTED = u'submitted'
    APPROVED = u'approved'
    COMPLETED = u'completed'
    CANCELLED = u'cancelled'
    STATUS = (
        (DRAFT, u"Draft"),
        (PLANNED, u"Planned"),
        (SUBMITTED, u"Submitted"),
        (APPROVED, u"Approved"),
        (COMPLETED, u"Completed"),
        (CANCELLED, u"Cancelled"),
    )

    plan = models.ForeignKey(SupplyPlan)
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=DRAFT,
    )
    to_review = models.BooleanField(blank=True, default=False)
    reviewed = models.BooleanField(blank=True, default=False)
    review_date = models.DateField(
        null=True, blank=True
    )
    reviewed_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    review_comments = models.TextField(
        null=True, blank=True,
    )
    to_validate = models.BooleanField(blank=True, default=False)
    validated = models.BooleanField(blank=True, default=False)
    validation_date = models.DateField(
        null=True, blank=True
    )
    validated_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    validation_comments = models.TextField(
        null=True, blank=True,
    )
    to_approve = models.BooleanField(blank=True, default=False)
    approved = models.BooleanField(blank=True, default=False)
    approval_date = models.DateField(
        null=True, blank=True
    )
    approved_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    approval_comments = models.TextField(
        null=True, blank=True,
    )
    comments = models.TextField(
        null=True, blank=True,
    )

    @property
    def plan_partner(self):
        return self.plan.partner

    @property
    def plan_partnership(self):
        return self.plan.pca

    @property
    def plan_section(self):
        return self.plan.section


class DistributionPlanItem(models.Model):
    """
    Distribution Fields
    """
    plan = models.ForeignKey(DistributionPlan, related_name='requests')
    wave_number = models.CharField(
        max_length=2,
        null=True, blank=False,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    wave = models.ForeignKey(WavePlan, null=True, blank=False)
    site = models.ForeignKey(Location, null=True, blank=False)
    purpose = models.CharField(
        max_length=50,
        null=True, blank=True,
        choices=Choices(
            ('emergency_request', 'Emergency Request',),
            ('pd_request', 'PD Request',),
        ),
        default='pd_request'
    )
    target_population = models.IntegerField(
        verbose_name=u'No. of beneficiaries covered',
        null=True, blank=True
    )
    delivery_location = models.ForeignKey(
        Location,
        null=True, blank=True,
        related_name='delivery_location'
    )
    contact_person = models.ForeignKey(
        PartnerStaffMember,
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
        return u'Wave {}: Quantity: {} - Site: {}'.format(
            self.wave_number,
            self.quantity_requested,
            self.site,
        )


class DistributionPlanWave(models.Model):
    plan = models.ForeignKey(DistributionPlanItem, related_name='supply_waves')
    # supply_item = models.ForeignKey(SupplyPlanItem, related_name='supply_items')
    supply_item = models.ForeignKey(SupplyItem, related_name='supply_items')
    quantity_required = models.PositiveIntegerField(
        help_text=u'Quantity required for this wave',
        null=True, blank=False
    )
    delivery_location = models.ForeignKey(
        Location,
        null=True, blank=True,
        related_name='item_delivery_location'
    )
    date_required_by = models.DateField(
        null=True, blank=False
    )
    date_distributed_by = models.DateField(
        verbose_name=u'planned distribution date',
        null=True, blank=True
    )

    def __unicode__(self):
        return u'{} - ({})'.format(
            self.supply_item.__unicode__(),
            self.quantity_required
        )


class DistributionPlanItemReceived(models.Model):
    """
    Distribution Fields
    """
    plan = models.ForeignKey(DistributionPlan, related_name='received')
    wave_number = models.CharField(
        max_length=2,
        null=True, blank=False,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    wave = models.ForeignKey(DistributionPlanItem, null=True, blank=False)
    quantity_received = models.PositiveIntegerField(
        null=True, blank=True
    )
    date_received = models.DateField(
        null=True, blank=True,
    )
    date_distributed = models.DateField(
        null=True, blank=True,
    )
    quantity_distributed = models.PositiveIntegerField(
        null=True, blank=True
    )

    def __unicode__(self):
        return u'{} {}'.format(
            self.wave_number,
            self.wave
        )
