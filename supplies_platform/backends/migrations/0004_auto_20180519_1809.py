# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-19 18:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backends', '0003_notification_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]