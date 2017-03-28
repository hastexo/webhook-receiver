# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigIntegerField(serialize=False, editable=False, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('first_name', models.CharField(max_length=254)),
                ('last_name', models.CharField(max_length=254)),
                ('received', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Unprocessed'), (1, b'Processing'), (2, b'Processed'), (3, b'Error')])),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sku', models.CharField(max_length=254)),
                ('email', models.EmailField(max_length=254)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Unprocessed'), (1, b'Processed'), (2, b'Error')])),
                ('order', models.ForeignKey(to='edx_shopify.Order')),
            ],
        ),
    ]
