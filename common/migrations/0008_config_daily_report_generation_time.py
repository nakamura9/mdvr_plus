# Generated by Django 2.2 on 2019-10-09 06:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_config_harsh_braking_delta'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='daily_report_generation_time',
            field=models.TimeField(default=datetime.time(23, 30)),
        ),
    ]