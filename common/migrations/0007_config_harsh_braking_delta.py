# Generated by Django 2.2 on 2019-10-01 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_config_speeding_threshold'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='harsh_braking_delta',
            field=models.FloatField(default=40.0),
        ),
    ]