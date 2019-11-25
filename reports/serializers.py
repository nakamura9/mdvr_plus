from rest_framework.serializers import ModelSerializer
from reports.models import Alarm, CalendarReminderAlert, MileageReminderAlert

class AlarmSerializer(ModelSerializer):
    class Meta:
        model = Alarm
        fields = "__all__"

class CalendarReminderAlertSerializer(ModelSerializer):
    class Meta:
        model = CalendarReminderAlert
        fields = "__all__"


class MileageReminderAlertSerializer(ModelSerializer):
    class Meta:
        model = MileageReminderAlert
        fields = "__all__"