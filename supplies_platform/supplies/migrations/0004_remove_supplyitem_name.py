# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-26 19:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supplies', '0003_auto_20180226_1334'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplyitem',
            name='name',
        ),
    ]