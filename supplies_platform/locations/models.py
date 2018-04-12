from __future__ import unicode_literals

from django.db import models

from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey

from django.db import models


class LocationType(models.Model):
    type = models.CharField(max_length=254)

    def __str__(self):
        return self.type


class Location(MPTTModel):
    name = models.CharField(max_length=254)
    description = models.CharField(max_length=254)
    type = models.ForeignKey(LocationType, verbose_name='Location Type')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    # geom = models.MultiPolygonField(null=True, blank=True)
    # point = models.PointField(null=True, blank=True)
    # objects = models.GeoManager()

    def __unicode__(self):
        return u'{} - {}'.format(
            self.name,
            self.type.type
        )

    #
    # @property
    # def geo_point(self):
    #     return self.point if self.point else self.geom.point_on_surface


    # @property
    # def point_lat_long(self):
    #     return "Lat: {}, Long: {}".format(
    #         self.point.y,
    #         self.point.x
    #     )

    class Meta:
        unique_together = ('name', 'type')
        ordering = ['name']
