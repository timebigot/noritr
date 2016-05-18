# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-14 22:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('buysell', '0017_customer_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='buysell.Area'),
        ),
    ]
