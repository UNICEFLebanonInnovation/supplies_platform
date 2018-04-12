from __future__ import unicode_literals

from django.db import models

from supplies_platform.users.models import Section


class SupplyItem(models.Model):

    code = models.CharField(
        max_length=10,
    )
    description = models.TextField(
        blank=True
    )
    unit_of_measure = models.CharField(
        max_length=10,
        blank=True, null=True,
    )
    unit_weight = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True, null=True,
        help_text='KG'
    )
    unit_volume = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True, null=True,
        help_text='M3'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=9,
        blank=True, null=True,
        help_text='$'
    )
    quantity_in_stock = models.PositiveIntegerField(blank=True, null=True,)
    section = models.ForeignKey(Section)

    def __unicode__(self):
        return '{} - {} - {} - {} - {}'.format(
            self.code,
            self.description,
            self.price,
            self.quantity_in_stock,
            self.section
        )
