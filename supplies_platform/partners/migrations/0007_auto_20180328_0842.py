# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-28 08:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0006_auto_20180328_0842'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pca',
            old_name='partnership_type',
            new_name='document_type',
        ),
    ]
