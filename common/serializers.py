from rest_framework import serializers
from common.models import Config

class ConfigSerializer(serializers.ModelSerializer):
    host = serializers.SerializerMethodField()

    class Meta:
        model = Config
        fields = 'conn_account', 'conn_password','host', 'server_port'

    def get_host(self, obj):
        return obj.host