# Generated by Django 2.2 on 2019-09-16 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_config_smtp_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='DDC_reminder_days',
            field=models.IntegerField(default=30),
            preserve_default=False,
        ),
    ]