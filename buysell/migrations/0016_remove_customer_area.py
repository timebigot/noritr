# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-14 22:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buysell', '0015_auto_20160514_1844'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='area',
        ),
    ]
