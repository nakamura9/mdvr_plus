# Generated by Django 2.2 on 2019-10-06 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0011_auto_20191004_0051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleservice',
            name='interval_mileage',
            field=models.IntegerField(default=0),
        ),
    ]