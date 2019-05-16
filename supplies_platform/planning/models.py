from __future__ import unicode_literals

import datetime

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings
from django.db.models import Avg, Count, Min, Sum

from model_utils.choices import Choices
from model_utils.models import TimeStampedModel
from smart_selects.db_fields import ChainedForeignKey

from supplies_platform.locations.models import Location
from supplies_platform.users.models import User, Section
from supplies_platform.partners.models import PartnerOrganization, PartnerStaffMember, PCA
from supplies_platform.supplies.models import SupplyItem, SupplyService, Grant


class YearlySupplyPlan(TimeStampedModel):

    PLANNED = u'planned'
    SUBMITTED = u'submitted'
    REVIEWED = u'reviewed'
    APPROVED = u'approved'
    COMPLETED = u'completed'
    CANCELLED = u'cancelled'
    STATUS = (
        (PLANNED, u"Planned"),
        (SUBMITTED, u"Submitted"),
        (REVIEWED, u"Reviewed"),
        (APPROVED, u"Approved"),
        (COMPLETED, u"Completed"),
        (CANCELLED, u"Cancelled"),
    )

    reference_number = models.CharField(
        max_length=100,
        null=True, blank=True,
    )
    section = models.ForeignKey(
        Section,
        null=True, blank=False
    )
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=PLANNED,
    )
    year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
    )
    solicitation_method = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        choices=(
            ('Low Value', 'Low Value'),
            ('Request for Quotation (RFQ)', 'Request for Quotation (RFQ)'),
            ('Invitation To Bid (ITB)', 'Invitation To Bid (ITB)'),
            ('Request for Proposal (RFP)', 'Request for Proposal (RFP)'),
            ('Long Term Agreement (LTA)', 'Long Term Agreement (LTA)'),
            ('Direct Order', 'Direct Order'),
            ('Off shore (SD)', 'Off shore (SD)'),
        ),
    )
    activity_ref = models.CharField(
        max_length=254,
        null=True, blank=True,
    )
    submission_date = models.DateField(
        null=True, blank=True
    )
    to_review = models.BooleanField(blank=True, default=False)
    reviewed = models.NullBooleanField(null=True, blank=True, default=None)
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
    approved = models.NullBooleanField(null=True, blank=True, default=None)
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
        related_name='+',
        verbose_name='Modified by',
    )
    comments = models.TextField(
        null=True, blank=True,
    )
    tpm_focal_point = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+',
        verbose_name='TPM focal point',
    )

    @property
    def total_budget(self):
        total = 0.0
        total1 = 0.0
        try:
            items = self.supply_plan_items.all()
            for item in items:
                total += item.quantity * item.item.price
        except Exception as ex:
            pass

        try:
            items = self.supply_plan_services.all()
            for item in items:
                total1 += item.quantity * item.expected_amount
        except Exception as ex:
            pass

        return '{}$'.format(
            total + total1
        )

    @property
    def plan_section(self):
        return self.section

    def __unicode__(self):
        return '{} - {}'.format(
            self.reference_number,
            self.section
        )

    def get_path(self, tab):
        return 'https://supply-platform.herokuapp.com/admin/planning/yearlysupplyplan/{}/change/{}'.format(
            self.id,
            tab
        )

    def save(self, **kwargs):
        if not self.reference_number:
            year = datetime.date.today().year
            objects = list(YearlySupplyPlan.objects.filter(
                created__year=year,
            ).order_by('created').values_list('id', flat=True))
            sequence = '{0:02d}'.format(objects.index(self.id) + 1 if self.id in objects else len(objects) + 1)
            self.reference_number = '{}{}{}'.format(
                'YSP',
                year,
                sequence
            )

        super(YearlySupplyPlan, self).save(**kwargs)


class SupplyPlanItem(models.Model):

    plan = models.ForeignKey(
        YearlySupplyPlan,
        null=True, blank=True,
        related_name='supply_plan_items'
    )
    item = models.ForeignKey(SupplyItem)
    quantity = models.PositiveIntegerField(
        help_text=u'PD Quantity'
    )
    grant = models.ForeignKey(Grant, null=True, blank=True)
    expiry_date = models.DateField(
        null=True, blank=True
    )
    solicitation_method = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        choices=(
            ('Low Value', 'Low Value'),
            ('Request for Quotation (RFQ)', 'Request for Quotation (RFQ)'),
            ('Invitation To Bid (ITB)', 'Invitation To Bid (ITB)'),
            ('Request for Proposal (RFP)', 'Request for Proposal (RFP)'),
            ('Long Term Agreement (LTA)', 'Long Term Agreement (LTA)'),
            ('Direct Order', 'Direct Order'),
            ('Off shore (SD)', 'Off shore (SD)'),
        ),
    )
    activity_reference = models.CharField(
        max_length=254,
        null=True, blank=True,
    )

    @property
    def beneficiaries_covered_per_item(self):
        ttl = 0
        if self.supply_plan:
            plans = DistributionPlanWave.objects.filter(
                plan__plan_id=self.supply_plan_id,
                wave__supply_plan__item_id=self.item_id
            )
            for item in plans:
                ttl += item.target_population
        return ttl

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
            self.plan.__unicode__(),
            self.item,
            self.quantity
        )


class SupplyPlanGrant(models.Model):

    plan = models.ForeignKey(
        YearlySupplyPlan,
        null=True, blank=True,
        related_name='supply_plan_grants'
    )
    grant = models.ForeignKey(Grant)
    expiry_date = models.DateField(
        null=True, blank=True
    )


class SupplyPlanService(models.Model):

    plan = models.ForeignKey(
        YearlySupplyPlan,
        null=True, blank=True,
        related_name='supply_plan_services'
    )
    item = models.ForeignKey(SupplyService)
    expected_amount = models.FloatField(
        blank=True, null=True,
        verbose_name='Expected Amount/Unit Price',
        help_text='$'
    )
    quantity = models.PositiveIntegerField(
        help_text=u'PD Quantity'
    )
    grant = models.ForeignKey(Grant, null=True, blank=True)
    expiry_date = models.DateField(
        null=True, blank=True
    )
    solicitation_method = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        choices=(
            ('Low Value', 'Low Value'),
            ('Request for Quotation (RFQ)', 'Request for Quotation (RFQ)'),
            ('Invitation To Bid (ITB)', 'Invitation To Bid (ITB)'),
            ('Request for Proposal (RFP)', 'Request for Proposal (RFP)'),
            ('Long Term Agreement (LTA)', 'Long Term Agreement (LTA)'),
            ('Direct Order', 'Direct Order'),
            ('Off shore (SD)', 'Off shore (SD)'),
        ),
    )
    activity_reference = models.CharField(
        max_length=254,
        null=True, blank=True,
    )

    @property
    def total_budget(self):
        total = 0.0
        try:
            total = self.quantity * self.expected_amount
        except Exception as ex:
            pass
        return '{} {}'.format(
            total,
            '$'
        )

    def __unicode__(self):
        return u'{}-{}-{}-{}$'.format(
            self.plan.__unicode__(),
            self.item,
            self.quantity,
            self.expected_amount
        )


class SupplyPlan(TimeStampedModel):

    PLANNED = u'planned'
    SUBMITTED = u'submitted'
    REVIEWED = u'reviewed'
    APPROVED = u'approved'
    COMPLETED = u'completed'
    CANCELLED = u'cancelled'
    STATUS = (
        (PLANNED, u"Planned"),
        (SUBMITTED, u"Submitted"),
        (REVIEWED, u"Reviewed"),
        (APPROVED, u"Approved"),
        (COMPLETED, u"Completed"),
        (CANCELLED, u"Cancelled"),
    )

    supply_plan = models.ForeignKey(YearlySupplyPlan, related_name='yearly_plan')
    reference_number = models.CharField(
        max_length=100,
        null=True, blank=True,
    )

    partnership = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=''
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        null=True, blank=True,
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
        default=PLANNED,
    )
    is_for_internal = models.BooleanField(
        blank=True,
        default=False,
        verbose_name='Is for Internal use?',
    )
    submission_date = models.DateField(
        null=True, blank=True
    )
    to_review = models.BooleanField(blank=True, default=False)
    reviewed = models.NullBooleanField(null=True, blank=True, default=None)
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
    approved = models.NullBooleanField(null=True, blank=True, default=None)
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
    tpm_focal_point = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+',
        verbose_name='TPM focal point',
    )

    items = models.ManyToManyField(SupplyItem, blank=True)
    wave_number = models.PositiveIntegerField(
        null=True, blank=True,
        choices=Choices(
            1, 2, 3, 4
        ),
        verbose_name='Number of waves',
    )
    services = models.ManyToManyField(SupplyService, blank=True)

    @property
    def target_population(self):
        ttl = 0
        plans = DistributionPlanWave.objects.filter(
            plan__plan_id=self.id,
        )
        for item in plans:
            ttl += item.target_population
        return ttl

    @property
    def total_budget(self):
        total = 0.0
        try:
            items = self.waves_items.all()
            for item in items:
                total += item.quantity * item.item.price
        except Exception as ex:
            pass
        return '{} {}'.format(
            total,
            '$'
        )

    @property
    def plan_section(self):
        return self.section

    def __unicode__(self):
        return '{} - {}'.format(
            self.reference_number,
            self.section
        )

    def get_path(self, tab):
        return 'https://supply-platform.herokuapp.com/admin/planning/supplyplan/{}/change/{}'.format(
            self.id,
            tab
        )

    def save(self, **kwargs):
        if not self.reference_number:
            year = datetime.date.today().year
            objects = list(SupplyPlan.objects.filter(
                created__year=year,
            ).order_by('created').values_list('id', flat=True))
            sequence = '{0:02d}'.format(objects.index(self.id) + 1 if self.id in objects else len(objects) + 1)
            self.reference_number = '{}{}{}'.format(
                'SP',
                year,
                sequence
            )

        super(SupplyPlan, self).save(**kwargs)


class SupplyPlanWave(models.Model):

    supply_plan = models.ForeignKey(SupplyPlan, related_name='supply_plans_waves')
    wave_number = models.CharField(
        max_length=2,
        null=True, blank=False,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    date_required_by = models.DateField(
        null=True, blank=False
    )

    def __unicode__(self):
        return u'Wave #{} - {}'.format(
            self.wave_number,
            self.date_required_by,
        )


class SupplyPlanWaveItem(models.Model):

    plan = models.ForeignKey(
        SupplyPlan,
        null=True, blank=True,
        related_name='waves_items'
    )
    plan_wave = models.ForeignKey(SupplyPlanWave, related_name='supply_plan_wave_items')
    item = models.ForeignKey(SupplyItem)
    quantity = models.PositiveIntegerField(
        help_text=u'PD Quantity'
    )

    @property
    def beneficiaries_covered_per_item(self):
        ttl = 0
        if self.supply_plan:
            plans = DistributionPlanWave.objects.filter(
                plan__plan_id=self.supply_plan_id,
                wave__supply_plan__item_id=self.item_id
            )
            for item in plans:
                ttl += item.target_population
        return ttl

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
            self.plan_wave.__unicode__(),
            self.item,
            self.quantity
        )


class DistributionPlan(TimeStampedModel):

    PLANNED = u'planned'
    SUBMITTED = u'submitted'
    REVIEWED = u'reviewed'
    CLEARED = u'cleared'
    APPROVED = u'approved'
    COMPLETED = u'completed'
    RECEIVED = u'received'
    CANCELLED = u'cancelled'
    STATUS = (
        (PLANNED, u"Planned"),
        (SUBMITTED, u"Submitted/Plan completed"),
        (REVIEWED, u"Reviewed"),
        (CLEARED, u"Cleared"),
        (APPROVED, u"Approved"),
        # (RECEIVED, u"All waves received"),
        # (COMPLETED, u"Distribution Completed"),
        (CANCELLED, u"Cancelled"),
    )

    reference_number = models.CharField(
        max_length=100,
        null=True, blank=True,
    )
    plan = models.ForeignKey(SupplyPlan, related_name='plan')
    yearly_plan = models.ForeignKey(YearlySupplyPlan, related_name='yearly_dist_plan', null=True, blank=True)
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default=PLANNED,
    )
    submitted = models.BooleanField(blank=True, default=False)
    submission_date = models.DateField(
        null=True, blank=True
    )
    submitted_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    to_review = models.BooleanField(blank=True, default=False)
    reviewed = models.NullBooleanField(null=True, blank=True, default=None)
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
    validated = models.NullBooleanField(null=True, blank=True, default=None)
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
    to_cleared = models.BooleanField(blank=True, default=False)
    cleared = models.NullBooleanField(null=True, blank=True, default=None)
    cleared_date = models.DateField(
        null=True, blank=True
    )
    cleared_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    cleared_comments = models.TextField(
        null=True, blank=True,
    )
    to_approve = models.BooleanField(blank=True, default=False)
    approved = models.NullBooleanField(null=True, blank=True, default=None)
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
    to_delivery = models.BooleanField(blank=True, default=False)
    delivery_expected_date = models.DateField(
        null=True, blank=True
    )
    item_received = models.BooleanField(blank=True, default=False)
    item_received_date = models.DateField(
        null=True, blank=True
    )
    item_distributed = models.BooleanField(blank=True, default=False)
    item_distributed_date = models.DateField(
        null=True, blank=True
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

    def __unicode__(self):
        return '{} - {} - {}'.format(
            self.reference_number,
            self.plan.partner,
            self.plan.section
        )

    def get_path(self, tab):
        return 'https://supply-platform.herokuapp.com/admin/planning/distributionplan/{}/change/{}'.format(
            self.id,
            tab
        )

    def save(self, **kwargs):
        if not self.reference_number:
            year = datetime.date.today().year
            objects = list(DistributionPlan.objects.filter(
                created__year=year,
            ).order_by('created').values_list('id', flat=True))
            sequence = '{0:02d}'.format(objects.index(self.id) + 1 if self.id in objects else len(objects) + 1)
            self.reference_number = '{}/{}{}{}'.format(
                self.plan.reference_number,
                'DP',
                year,
                sequence
            )

        super(DistributionPlan, self).save(**kwargs)


class DistributionPlanWave(TimeStampedModel):

    plan = models.ForeignKey(DistributionPlan, related_name='plan_waves')
    wave_number = models.CharField(
        max_length=2,
        null=True, blank=False,
        choices=Choices(
            '1', '2', '3', '4'
        )
    )
    wave = models.ForeignKey(SupplyPlanWave, null=True, blank=False)
    site = models.ForeignKey(
        Location,
        null=True, blank=True,
        verbose_name=u'Distribution site',
    )
    purpose = models.CharField(
        max_length=50,
        null=True, blank=True,
        choices=Choices(
            ('emergency_request', 'Emergency Request',),
            ('pd_request', 'PD Request',),
        ),
        default='pd_request'
    )
    delivery_site = models.ForeignKey(
        Location,
        null=True, blank=True,
        related_name='delivery_site',
        help_text=u'Leave it empty if the same save the Site above',
    )
    contact_person = models.ForeignKey(
        PartnerStaffMember,
        null=True, blank=True
    )
    date_required_by = models.DateField(
        null=True, blank=True,
    )
    to_delivery = models.BooleanField(blank=True, default=False)
    delivery_expected_date = models.DateField(
        null=True, blank=True,
        help_text='To be defined by UNICEF Supply Beirut focal point'
    )

    def __unicode__(self):
        return u'Wave #{} - Delivery expected date: {}'.format(
            self.wave_number,
            self.delivery_expected_date if self.delivery_expected_date else ''
        )


class DistributionPlanWaveItem(models.Model):

    plan_wave = models.ForeignKey(DistributionPlanWave, related_name='plan_wave_items')
    wave_item = models.ForeignKey(SupplyPlanWaveItem, null=True, blank=False)
    item = models.ForeignKey(SupplyItem, related_name='items_distribution_waves')
    quantity_requested = models.PositiveIntegerField(
        verbose_name=u'Quantity required',
        null=True, blank=False
    )
    target_population = models.IntegerField(
        verbose_name=u'No. of beneficiaries covered',
        null=True, blank=True
    )
    date_distributed_by = models.DateField(
        verbose_name=u'planned distribution date',
        null=True, blank=True
    )


class DistributionPlanItemReceived(TimeStampedModel):

    plan = models.ForeignKey(DistributionPlan, related_name='received')
    supply_item = models.ForeignKey(SupplyItem, related_name='received_items')
    wave_plan = models.ForeignKey(DistributionPlanWave, null=True, blank=True, related_name='received_wave_plan')
    wave_item = models.ForeignKey(DistributionPlanWaveItem, null=True, blank=True, related_name='received_wave_item')
    quantity_requested = models.PositiveIntegerField(
        null=True, blank=True
    )
    quantity_received = models.PositiveIntegerField(
        null=True, blank=True
    )
    date_received = models.DateField(
        null=True, blank=True,
    )
    wave_number = models.CharField(
        max_length=2,
        null=True, blank=False,
    )

    def __unicode__(self):
        return u'{} - {} - {}'.format(
            self.plan,
            self.supply_item,
            self.quantity_received
        )


class DistributedItem(TimeStampedModel):

    plan = models.ForeignKey(DistributionPlan, related_name='distributed')
    supply_item = models.ForeignKey(SupplyItem, related_name='distributed_items')
    wave_plan = models.ForeignKey(DistributionPlanWave, null=True, blank=True, related_name='distributed_wave_plan')
    wave_item = models.ForeignKey(DistributionPlanWaveItem, null=True, blank=True, related_name='distributed_wave_item')
    quantity_distributed_per_site = models.PositiveIntegerField(
        null=True, blank=True
    )
    wave_number = models.CharField(
        max_length=2,
        null=True, blank=False,
    )
    quantity_requested = models.PositiveIntegerField(
        null=True, blank=True
    )

    def __unicode__(self):
        return u'{} - {}'.format(
            self.plan,
            self.supply_item
        )


class DistributedItemSite(models.Model):

    plan = models.ForeignKey(DistributedItem, related_name='distributed_sites')
    site = models.ForeignKey(Location, blank=False)
    quantity_distributed_per_site = models.PositiveIntegerField(
        null=True, blank=True
    )
    distribution_date = models.DateField(
        null=True, blank=True
    )
    tpm_visit = models.BooleanField(
        blank=True, default=False,
        verbose_name=u'TPM Visit?',
        help_text=u'TPM visit for this location',
    )
    tpm_focal_point = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+',
        verbose_name='TPM focal point',
    )
    unicef_visit = models.BooleanField(
        blank=True, default=False,
        verbose_name=u'UNICEF Visit?',
        help_text=u'UNICEF visit for this location',
    )

    def __unicode__(self):
        return u'{} - {} - {} - {}'.format(
            self.plan.supply_item.code,
            self.site,
            self.quantity_distributed_per_site,
            self.distribution_date,
        )
