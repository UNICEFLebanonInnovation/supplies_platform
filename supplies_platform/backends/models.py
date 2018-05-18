from __future__ import unicode_literals, absolute_import, division

from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.utils.encoding import force_text

from model_utils.models import TimeStampedModel
from model_utils import Choices


class Notification(TimeStampedModel):

    name = models.CharField(
        max_length=500,
        blank=False, null=True
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
        max_length=50,
        blank=True, null=True
    )
    user_group = models.CharField(
        max_length=50,
        blank=True, null=True
    )
    object_id = models.CharField(
        max_length=50,
        blank=True, null=True
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
