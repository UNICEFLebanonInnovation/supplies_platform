from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings

from model_utils.choices import Choices
from model_utils.models import TimeStampedModel
from smart_selects.db_fields import ChainedForeignKey

from supplies_platform.locations.models import Location
from supplies_platform.users.models import User
from supplies_platform.supplies.models import SupplyItem
from supplies_platform.planning.models import DistributionPlan
from supplies_platform.planning.models import SupplyPlan
from supplies_platform.users.util import generate_hash


class TPMVisit(TimeStampedModel):

    supply_plan = models.ForeignKey(SupplyPlan, related_name='+')
    distribution_plan = models.ForeignKey(DistributionPlan, related_name='+')
    supply_item = models.ForeignKey(SupplyItem, blank=False, related_name='+')
    site = models.ForeignKey(Location, blank=False, related_name='+')
    quantity_distributed = models.PositiveIntegerField(
        null=True, blank=True
    )
    distribution_date = models.DateField(
        null=True, blank=True
    )

    quantity_assessment = JSONField(blank=True, null=True)
    quantity_assessment_completed = models.BooleanField(blank=True, default=False)
    quantity_assessment_completed_date = models.DateTimeField(
        blank=True, null=True
    )
    quality_assessment = JSONField(blank=True, null=True)
    quality_assessment_completed = models.BooleanField(blank=True, default=False)
    quality_assessment_completed_date = models.DateTimeField(
        blank=True, null=True
    )
    requested_by = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    assigned_to_officer = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )
    assigned_to_tpm = models.ForeignKey(
        User,
        null=True, blank=True,
        related_name='+'
    )

    class Meta:
        ordering = ['created']
        verbose_name = 'SM Visit'
        verbose_name_plural = 'SM Visits'

    def __unicode__(self):
        return u'{} - {} - {}'.format(
            self.supply_plan.partner,
            self.site,
            self.supply_item
        )

    @property
    def supply_plan_partner(self):
        return self.supply_plan.partner

    @property
    def supply_plan_partnership(self):
        return self.supply_plan.pca

    @property
    def supply_plan_section(self):
        return self.supply_plan.section


class AssessmentHash(models.Model):

    hashed = models.CharField(max_length=100, unique=True)
    tpm_visit = models.CharField(max_length=20)
    assessment_slug = models.CharField(max_length=50)
    user = models.CharField(max_length=20)
    timestamp = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']

    @property
    def name(self):
        return '{}{}{}{}'.format(
            self.tpm_visit,
            self.assessment_slug,
            self.user,
            self.timestamp,
        )

    def __unicode__(self):
        return '{}-{}-{}-{}-{}'.format(
            self.hashed,
            self.tpm_visit,
            self.assessment_slug,
            self.user,
            self.timestamp,
        )

    def save(self, **kwargs):
        """
        Generate unique Hash for every assessment
        :param kwargs:
        :return:
        """
        if self.pk is None:
            self.hashed = generate_hash(self.name)

        super(AssessmentHash, self).save(**kwargs)
