# Generated by Django 5.1.3 on 2024-11-20 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beposoft_app', '0079_grvmodel_date_grvmodel_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='grvmodel',
            name='updated_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
