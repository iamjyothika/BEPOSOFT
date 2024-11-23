# Generated by Django 5.1.3 on 2024-11-22 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beposoft_app', '0080_grvmodel_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='date',
        ),
        migrations.AlterField(
            model_name='grvmodel',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='updated_at',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]