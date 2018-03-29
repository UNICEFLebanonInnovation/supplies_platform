# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-28 08:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0005_auto_20180328_0829'),
    ]

    operations = [
        migrations.AddField(
            model_name='pca',
            name='partner_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='pca',
            name='partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='partners.PartnerOrganization'),
        ),
    ]
