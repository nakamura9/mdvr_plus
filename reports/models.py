from django.db import models
from django.shortcuts import reverse 
# Create your models here.
class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('earth-mover', 'Earth Moving Equipment'),
    ]
    registration_number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=16, choices=VEHICLE_TYPES)
    

    def __str__(self):
        return self.name

    @property
    def reminders(self):
        return self.reminder_set.all()

    def get_absolute_url(self):
        return reverse("reports:vehicle-details", kwargs={"pk": self.pk})
    


class Reminder(models.Model):
    REMINDER_CHOICES = [
        ('service', 'Vehicle Service'),
        ('certificate-of-fitness', 'Vehicle Certificate of Fitness')
    ]
    vehicle = models.ForeignKey('reports.vehicle', 
        on_delete=models.SET_NULL,
        null=True)
    date = models.DateField()
    reminder_type = models.CharField(max_length=64, choices=REMINDER_CHOICES)
    interval_days = models.IntegerField(default=180)
    interval_mileage = models.IntegerField(default=5000)
    reminder_email = models.EmailField()
    reminder_message = models.TextField()
    active = models.BooleanField(default=True)
    last_reminder = models.DateField(null=True, blank=True)


    def repeat_on_date(self, date):
        if date > self.date:
            delta = (date - self.date).days
            if delta % self.interval_days == 0:
                return True
            
        return False