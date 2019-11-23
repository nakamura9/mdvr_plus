from rest_framework.serializers import ModelSerializer
from reports.models import Alarm, ReminderEvent

class AlarmSerializer(ModelSerializer):
    class Meta:
        model = Alarm
        fields = "__all__"

class ReminderEventSerializer(ModelSerializer):
    class Meta:
        model = ReminderEvent
        fields = "__all__"