from django_filters import FilterSet
from . import models


class ReminderFilter(FilterSet):
    class Meta:
        model = models.Reminder
        fields = {
            'date': ['exact'],
            'reminder_type': ['exact'],
            'vehicle__name': ['icontains'],
            'active': ['exact']
        }


class DriverFilter(FilterSet):
    class Meta:
        model = models.Driver
        fields = {
            'last_name': ['icontains'],
            'gender': ['exact'],
            
        }


class VehicleFilter(FilterSet):
    class Meta:
        model = models.Vehicle
        fields = {
            'name': ['icontains'],
            'make': ['icontains'],
            'model': ['icontains'],
            'year': ['exact', 'gt', 'lt']
            
        }