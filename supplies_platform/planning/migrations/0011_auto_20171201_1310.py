# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-01 13:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0010_distributionplanitem_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributionplanitem',
            name='target_population',
            field=models.IntegerField(blank=True, null=True, verbose_name='No. of beneficiaries covered'),
        ),
        migrations.AlterField(
            model_name='distributionplanitem',
            name='date_distributed_by',
            field=models.DateField(blank=True, null=True, verbose_name='planned distribution date'),
        ),
        migrations.AlterField(
            model_name='distributionplanitem',
            name='quantity_requested',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantity required for this location'),
        ),
        migrations.AlterField(
            model_name='supplyplanitem',
            name='covered_per_item',
            field=models.IntegerField(blank=True, null=True, verbose_name='Beneficiaries covered per item'),
        ),
        migrations.AlterField(
            model_name='supplyplanitem',
            name='target_population',
            field=models.IntegerField(blank=True, null=True, verbose_name='Max No. of beneficiaries covered'),
        ),
    ]