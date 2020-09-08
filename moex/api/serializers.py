from rest_framework import serializers
from ..models import Security


class SecurityRetrivieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        exclude = ['parce_url',
                   'board',
                   'engine',
                   'market',
                   'oldest_date',
                   'monitor']


class SecurityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = ["id",
                  "name",
                  "security_type",
                  "secid",
                  "emitent",
                  "today_price",
                  "last_update"]
