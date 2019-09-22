# Generated by Django 2.2 on 2019-09-17 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_drivermedical_vehiclecertificateoffitness'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='notes',
            field=models.ManyToManyField(blank=True, to='reports.Note'),
        ),
        migrations.AlterField(
            model_name='driver',
            name='vehicles',
            field=models.ManyToManyField(blank=True, to='reports.Vehicle'),
        ),
        migrations.AlterField(
            model_name='drivermedical',
            name='notes',
            field=models.ManyToManyField(blank=True, to='reports.Note'),
        ),
        migrations.AlterField(
            model_name='insurance',
            name='notes',
            field=models.ManyToManyField(blank=True, to='reports.Note'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='notes',
            field=models.ManyToManyField(blank=True, to='reports.Note'),
        ),
        migrations.AlterField(
            model_name='vehiclecertificateoffitness',
            name='notes',
            field=models.ManyToManyField(blank=True, to='reports.Note'),
        ),
        migrations.AlterField(
            model_name='vehicleservicelog',
            name='notes',
            field=models.ManyToManyField(blank=True, to='reports.Note'),
        ),
    ]
