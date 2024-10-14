# Generated by Django 5.1 on 2024-09-10 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beposoft_app', '0017_alter_user_allocated_states'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='city',
            new_name='state',
        ),
        migrations.AlterField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, default='india', max_length=100, null=True),
        ),
    ]