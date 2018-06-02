# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-06-02 11:28
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('planning', '0092_auto_20180602_1115'),
        ('locations', '0006_auto_20180417_0752'),
        ('supplies', '0008_auto_20180426_1310'),
        ('tpm', '0007_auto_20180514_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMVisit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('quantity_distributed', models.PositiveIntegerField(blank=True, null=True)),
                ('distribution_date', models.DateField(blank=True, null=True)),
                ('type', models.CharField(choices=[('quantity', 'Quantity'), ('quality', 'Quality')], max_length=2, null=True)),
                ('assessment', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('assessment_completed', models.BooleanField(default=False)),
                ('assessment_completed_date', models.DateTimeField(blank=True, null=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('distribution_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='planning.DistributionPlan')),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='locations.Location')),
                ('supply_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='supplies.SupplyItem')),
                ('supply_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='planning.SupplyPlan')),
            ],
            options={
                'ordering': ['created'],
                'verbose_name': 'SM Visit',
                'verbose_name_plural': 'SM Visits',
            },
        ),
    ]
