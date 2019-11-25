from django_filters import FilterSet
from . import models


class CalendarReminderFilter(FilterSet):
    class Meta:
        model = models.CalendarReminder
        fields = {
            'date': ['exact'],
            'repeatable': ['exact'],
            'vehicle__name': ['icontains'],
            'driver': ['exact'],
        }


class MileageReminderFilter(FilterSet):
    class Meta:
        model = models.MileageReminder
        fields = {
            'repeat_interval_mileage': ['exact'],
            'repeatable': ['exact'],
            'vehicle__name': ['icontains'],
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