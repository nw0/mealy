# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-11 15:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mealy', '0003_auto_20160409_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='cooking_style',
            field=models.CharField(choices=[(b'frying', b'Fried'), (b'boiling', b'Boiled'), (b'baking', b'Baked'), (b'roasting', b'Roasted'), (b'uncooked', b'Processed'), (b'instant', b'Microwaved')], max_length=8),
        ),
        migrations.AlterField(
            model_name='resource_inst',
            name='amt_original',
            field=models.FloatField(),
        ),
    ]
