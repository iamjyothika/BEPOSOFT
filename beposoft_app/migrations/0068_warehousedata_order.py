# Generated by Django 5.0.6 on 2024-11-14 04:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beposoft_app', '0067_warehousedata_parcel_service_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehousedata',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beposoft_app.order'),
        ),
    ]
