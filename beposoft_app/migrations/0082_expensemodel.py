# Generated by Django 5.1.3 on 2024-11-22 07:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beposoft_app', '0081_remove_order_date_alter_grvmodel_updated_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_mode', models.TextField()),
                ('expense_date', models.DateField()),
                ('transcation_id', models.IntegerField()),
                ('description', models.TextField()),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beposoft_app.bank')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beposoft_app.company')),
                ('payed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beposoft_app.user')),
            ],
        ),
    ]