# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-05-02 14:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplies', '0010_supplyservice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplyservice',
            name='code',
            field=models.CharField(max_length=10, verbose_name='Name'),
        ),
    ]
