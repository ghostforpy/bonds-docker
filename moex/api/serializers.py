from rest_framework import serializers
from ..models import Security, SecurityPortfolios, TradeHistory


class SecurityRetrivieSerializer(serializers.ModelSerializer):
    """ Serializer for retrivie one security"""
    faceunit = serializers.CharField(source='get_faceunit_display')

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
    faceunit = serializers.CharField(source='get_faceunit_display')

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


class SecurityInPortfolioSerializer(serializers.HyperlinkedModelSerializer):
    "serializer for SecurityPortfolios model"
    security_name = serializers.CharField(source='security')
    security_faceunit = serializers.CharField(source='security.get_faceunit_display')

    class Meta:
        model = SecurityPortfolios
        exclude = [
            'owner',
            'url',
            'portfolio'
        ]
        extra_kwargs = {
            'security': {"view_name": "api:security-detail"}
        }
        read_only_fields = [
            'security_name',
            'security_faceunit',
            'security',
            'count',
            'today_price',
            'total_cost'
        ]


class TradeHistorySerializerForPortfolioDetail(serializers.HyperlinkedModelSerializer):
    security_name = serializers.CharField(source='security')
    security_faceunit = serializers.CharField(source='security.get_faceunit_display')
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = TradeHistory
        exclude = ['url', 'portfolio', 'owner']
        extra_kwargs = {
            'security': {'view_name': 'api:security-detail'},
        }


class TradeHistorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TradeHistory
        exclude = ['url']
        extra_kwargs = {
            'security': {'view_name': 'api:security-detail'},
            'portfolio': {'view_name': 'api:investmentportfolio-detail'},
            'owner': {"view_name": "api:user-detail",
                      'lookup_field': 'username'}
        }
