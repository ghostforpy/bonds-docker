from rest_framework import serializers
from rest_framework.reverse import reverse
from ..models import Security, SecurityPortfolios, TradeHistory


class SecurityHistory(serializers.Serializer):
    date = serializers.DateField()
    price = serializers.FloatField()


class TradeHistorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TradeHistory
        exclude = ['url']
        extra_kwargs = {
            'security': {'view_name': 'api:securities-detail'},
            'portfolio': {'view_name': 'api:investmentportfolio-detail'},
            'owner': {"view_name": "api:user-detail",
                      'lookup_field': 'username'}
        }


class PortfolioNameUrlMixin(serializers.ModelSerializer):
    portfolio_url = serializers.SerializerMethodField()
    portfolio_name = serializers.CharField(source='portfolio')

    def get_portfolio_url(self, obj):
        return obj.portfolio.get_absolute_url()


class TradeHistorySerializerForSecurityDetail(PortfolioNameUrlMixin):
    url_for_delete = serializers.HyperlinkedIdentityField(
        view_name="api:securities-trade-history-detail")

    class Meta:
        model = TradeHistory
        exclude = ['security', 'owner']


class SecurityInPortfolioSerializerForSecurityDetail(PortfolioNameUrlMixin):
    class Meta:
        model = SecurityPortfolios
        exclude = ['security', 'today_price', 'owner']


class AllUserPortfoliosMixin(serializers.ModelSerializer):
    all_portfolios = serializers.SerializerMethodField()

    def get_all_portfolios(self, obj):
        user_portfolios = self.context['request'].user.portfolios.filter(
            manual=False).defer("id", "title")
        return {i.id: i.title for i in user_portfolios}


class NewSecurityRetrivieSerializer(AllUserPortfoliosMixin):
    """ Serializer for retrivie one security"""
    faceunit = serializers.CharField(source='get_faceunit_display')

    class Meta:
        model = Security
        exclude = ['parce_url',
                   'board',
                   'engine',
                   'market',
                   'oldest_date',
                   'monitor',
                   'source']


class SimpleSecurityRetrivieSerializer(serializers.ModelSerializer):
    """ Serializer for retrivie one security"""
    faceunit = serializers.CharField(source='get_faceunit_display')

    class Meta:
        model = Security
        exclude = ['parce_url',
                   'board',
                   'engine',
                   'market',
                   'oldest_date',
                   'monitor',
                   'source']


class SecurityRetrivieSerializer(AllUserPortfoliosMixin):
    """ Serializer for retrivie one security"""
    faceunit = serializers.CharField(source='get_faceunit_display')
    trades = TradeHistorySerializerForSecurityDetail(many=True)
    portfolios = SecurityInPortfolioSerializerForSecurityDetail(many=True)
    is_followed = serializers.SerializerMethodField()
    follow_url = serializers.HyperlinkedIdentityField(
        view_name="api:securities-follow")

    class Meta:
        model = Security
        exclude = ['parce_url',
                   'board',
                   'engine',
                   'market',
                   'oldest_date',
                   'monitor',
                   'source']

    def get_is_followed(self, obj):
        return self.context['request'].user in obj.users_follows.all()


class SecurityListSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for list securities """
    url = serializers.CharField(source='get_absolute_url')
    faceunit = serializers.CharField(source='get_faceunit_display')

    class Meta:
        model = Security
        fields = ["pk",
                  "name",
                  "security_type",
                  "secid",
                  "isin",
                  "emitent",
                  "today_price",
                  "last_update",
                  "faceunit",
                  "main_board_faceunit",
                  'url',
                  'issuesize',
                  'change_price_percent']


class NewSecurityListSerializer(serializers.Serializer):
    name = serializers.CharField()
    shortname = serializers.CharField()
    security_type = serializers.CharField()
    secid = serializers.CharField()
    isin = serializers.CharField()
    emitent = serializers.CharField()
    api_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    def get_api_url(self, obj):
        return reverse('api:securities-get-new', args=[obj.isin])

    def get_url(self, obj):
        return reverse('moex:new_detail_vue', args=[obj.isin])


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
            'security': {"view_name": "api:securities-detail"}
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
        #source='security.get_main_board_faceunit_display')
        source='get_currency_display')
    id = serializers.IntegerField(read_only=True)
    url_for_delete = serializers.HyperlinkedIdentityField(
        view_name='api:securities-trade-history-detail'
    )

    class Meta:
        model = TradeHistory
        exclude = ['url', 'portfolio', 'owner']
        extra_kwargs = {
            'security': {'view_name': 'api:securities-detail'},
        }


class TradeHistoryCreateSerializer(serializers.ModelSerializer):
    url_for_delete = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='api:securities-trade-history-detail')
    security_url = serializers.CharField(
        read_only=True, source='security.get_absolute_url')
    security_faceunit = serializers.CharField(
        read_only=True, source='security.main_board_faceunit')
    security_name = serializers.CharField(read_only=True, source='security')

    class Meta:
        model = TradeHistory
        exclude = ['owner']

    def create(self, validated_data):
        new_object = TradeHistory(**validated_data)
        create_status = new_object.save()
        if create_status == 'ok':
            return new_object
        else:
            return create_status


class TradeHistoryNewSecurityBuySerializer(TradeHistoryCreateSerializer):
    security_isin = serializers.CharField()

    class Meta(TradeHistoryCreateSerializer.Meta):
        exclude = TradeHistoryCreateSerializer.Meta.exclude + [
            'security', 'buy', 'ndfl'
        ]
