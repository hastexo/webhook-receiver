# Generated by Django 2.2.14 on 2020-07-22 10:58

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('webhook_receiver_shopify', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (1, 'Processing'), (2, 'Processed'), (-1, 'Error')], default=0),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (1, 'Processing'), (2, 'Processed'), (-1, 'Error')], default=0),
        ),
    ]