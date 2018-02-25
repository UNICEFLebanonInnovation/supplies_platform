from __future__ import unicode_literals

from django.db import models

from supplies_platform.users.models import Section


class SupplyItem(models.Model):

    code = models.CharField(
        max_length=10,
    )
    name = models.CharField(
        max_length=255,
    )
    description = models.TextField(
        blank=True
    )
    unit_of_measure = models.CharField(max_length=10)
    unit_weight = models.DecimalField(max_digits=3, decimal_places=2, help_text='KG')
    unit_volume = models.DecimalField(max_digits=3, decimal_places=2, help_text='M3')
    quantity_in_stock = models.PositiveIntegerField()
    section = models.ForeignKey(Section)

    def __unicode__(self):
        return '{} - {}'.format(self.name, self.code)
