# Generated by Django 5.1.3 on 2024-12-06 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beposoft_app', '0090_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='grvmodel',
            name='date',
            field=models.DateField(null=True),
        ),
    ]