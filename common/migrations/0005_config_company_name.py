# Generated by Django 2.2 on 2019-09-27 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_auto_20190921_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='company_name',
            field=models.CharField(default='Zimplats', max_length=255),
            preserve_default=False,
        ),
    ]