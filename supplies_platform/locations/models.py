from __future__ import unicode_literals

from django.db import models

from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey

from django.db import models


class LocationType(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name


class Location(MPTTModel):
    name = models.CharField(max_length=254)
    p_code = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=254, null=True, blank=True)
    type = models.ForeignKey(LocationType, verbose_name='Location Type')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __unicode__(self):
        return u'{} - {} ({})'.format(
            self.name,
            self.p_code,
            self.type.name
        )

    class Meta:
        unique_together = ('name', 'type')
        ordering = ['name']
