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
    price = models.FloatField(
        blank=True, null=True,
        verbose_name='Unit price',
        help_text='$'
    )
    quantity_in_stock = models.PositiveIntegerField(blank=True, null=True,)
    section = models.ForeignKey(Section, blank=True, null=True)

    @property
    def stock_value(self):
        if self.price and self.quantity_in_stock:
            return float(self.price * self.quantity_in_stock)
        return 0.0

    def __unicode__(self):
        return '{} - {} - {}$'.format(
            self.code,
            self.description,
            self.price,
            # self.quantity_in_stock,
            # self.section
        )


class SupplyService(models.Model):

    code = models.CharField(
        max_length=254,
        verbose_name='Name',
    )
    description = models.TextField(
        blank=True
    )
    expected_amount = models.FloatField(
        blank=True, null=True,
        verbose_name='Unit price',
        help_text='$'
    )

    def __unicode__(self):
        return '{} - {}'.format(
            self.code,
            self.description,
        )


class Grant(models.Model):

    name = models.CharField(
        max_length=254,
    )
