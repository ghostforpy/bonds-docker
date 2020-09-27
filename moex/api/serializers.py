from rest_framework import serializers
from ..models import Security


class SecurityRetrivieSerializer(serializers.ModelSerializer):
    """ Serializer for retrivie one security"""
    class Meta:
        model = Security
        exclude = ['parce_url',
                   'board',
                   'engine',
                   'market',
                   'oldest_date',
                   'monitor']


class SecurityListSerializer(serializers.ModelSerializer):
    """ Serializer for list securities """
    url = serializers.CharField(source='get_api_url', read_only=True)

    class Meta:
        model = Security
        fields = ["id",
                  "name",
                  "security_type",
                  "secid",
                  "isin",
                  "emitent",
                  "today_price",
                  "last_update",
                  "faceunit",
                  "url"]
