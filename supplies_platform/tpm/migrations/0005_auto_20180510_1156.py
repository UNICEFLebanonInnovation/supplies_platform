# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-10 11:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tpm', '0004_auto_20180510_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tpmvisit',
            name='quantity_distributed',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]