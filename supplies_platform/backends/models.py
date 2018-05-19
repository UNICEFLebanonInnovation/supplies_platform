from __future__ import unicode_literals, absolute_import, division

from django.conf import settings
from django.contrib.gis.db import models

from model_utils.models import TimeStampedModel

from supplies_platform.partners.models import PartnerOrganization


class Notification(TimeStampedModel):

    name = models.CharField(
        max_length=500,
        blank=True, null=True
    )
    subject = models.CharField(
        max_length=500,
        blank=False, null=True
    )
    type = models.CharField(
        max_length=50,
        blank=True, null=True
    )
    model = models.CharField(
        max_length=100,
        blank=True, null=True
    )
    user_group = models.CharField(
        max_length=100,
        blank=True, null=True
    )
    object_id = models.CharField(
        max_length=50,
        blank=True, null=True
    )
    send_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True, null=True,
        related_name='+',
    )
    status = models.BooleanField(blank=True, default=False)
    description = models.TextField(max_length=500, blank=True, null=True)
    comments = models.TextField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['created']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __unicode__(self):
        return self.name
