# Generated by Django 2.2.18 on 2021-02-09 08:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webhook_receiver', '0001_initial'),
        ('webhook_receiver_woocommerce', '0002_rename_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='woocommerceorder',
            name='webhook',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='webhook_receiver.JSONWebhookData'),
        ),
    ]
