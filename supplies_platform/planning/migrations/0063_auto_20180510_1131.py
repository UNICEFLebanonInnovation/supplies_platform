# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-10 11:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0062_auto_20180509_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributeditemsite',
            name='distribution_date',
            field=models.DateField(null=True),
        ),
    ]
