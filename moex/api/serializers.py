from rest_framework import serializers
from rest_framework.reverse import reverse
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


class SecurityListSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for list securities """
    url = serializers.HyperlinkedIdentityField(
        view_name="api:security-detail")
    faceunit = serializers.CharField(source='get_faceunit_display')
    main_board_faceunit = serializers.CharField(
        source='get_main_board_faceunit_display')

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
                  "main_board_faceunit"
                  'url',
                  'issuesize']


class SecurityBuyHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'moex:buy'
    queryset = Security.objects.all()

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'id': obj.pk
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class SecurityInPortfolioSerializer(serializers.HyperlinkedModelSerializer):
    "serializer for SecurityPortfolios model"
    security_name = serializers.CharField(source='security')
    security_url = serializers.CharField(source='security.get_absolute_url')
    security_faceunit = serializers.CharField(
        source='security.main_board_faceunit')
    security_type = serializers.CharField(
        source='security.security_type')
    shortname = serializers.CharField(
        source='security.shortname')
    security_change_price_percent = serializers.DecimalField(
        source='security.change_price_percent',
        max_digits=17,
        decimal_places=10
    )
    security_buy_url = serializers.SerializerMethodField()

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

    def get_security_buy_url(self, obj):
        return reverse('moex:buy', args=[obj.security.id])


class TradeHistorySerializerForPortfolioDetail(serializers.HyperlinkedModelSerializer):
    security_name = serializers.CharField(source='security')
    security_id = serializers.IntegerField(source='security.id',
                                           read_only=True)
    security_url = serializers.CharField(source='security.get_absolute_url')
    security_faceunit = serializers.CharField(
        source='security.get_main_board_faceunit_display')
    id = serializers.IntegerField(read_only=True)
    url_for_delete = serializers.HyperlinkedIdentityField(
        view_name='api:securities-trade-history-detail'
    )

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


class TradeHistoryCreateSerializer(serializers.HyperlinkedModelSerializer):
    security = serializers.CharField()
    portfolio = serializers.CharField()

    class Meta:
        model = TradeHistory
        exclude = ['owner']
        extra_kwargs = {
            'url': {'view_name': 'api:securities-trade-history-detail'},
        }

    def create(self, validated_data):
        new_object = TradeHistory(**validated_data)
        return new_object.save()
