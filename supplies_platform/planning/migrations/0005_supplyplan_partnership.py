# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-16 08:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0004_auto_20171116_0810'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplyplan',
            name='partnership',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]