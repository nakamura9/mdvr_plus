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