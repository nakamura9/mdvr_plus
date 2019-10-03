from rest_framework.serializers import ModelSerializer
from reports.models import Alarm

class AlarmSerializer(ModelSerializer):
    class Meta:
        model = Alarm
        fields = "__all__"