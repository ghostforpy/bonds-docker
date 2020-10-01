from rest_framework import serializers
from django.urls import reverse
from ..models import InvestmentPortfolio, PortfolioInvestHistory
from bonds.users.api.serializers import UserSerializer
from moex.api.serializers import SecurityInPortfolioSerializer,\
    TradeHistorySerializerForPortfolioDetail


class PortfolioInvestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioInvestHistory
        exclude = ['portfolio']


class InvestmentPortfolioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for create portfolio.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name="api:investmentportfolio-detail")

    class Meta:
        model = InvestmentPortfolio
        fields = ['title', 'private', 'strategia', 'manual', 'description', 'url']
        read_only_fields = ['url']

    def create(self, validated_data):
        new_object = InvestmentPortfolio(**validated_data)
        new_object.save()
        return new_object


class InvestmentPortfolioUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for update portfolio by owner.
    """
    class Meta:
        model = InvestmentPortfolio
        fields = ['today_cash', 'private']


class InvestmentPortfolioDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for view portfolio other users.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name="api:investmentportfolio-detail")
    owner_name = serializers.CharField(source="owner")

    class Meta:
        model = InvestmentPortfolio
        fields = ['owner',
                  'owner_name',
                  'url',
                  'title',
                  'invest_cash',
                  'today_cash',
                  'percent_profit',
                  'change_percent_profit',
                  'year_percent_profit',
                  'change_year_percent_profit',
                  'description',
                  'users_like',
                  'total_likes',
                  'users_follows',
                  'total_followers']
        extra_kwargs = {
            'users_follows': {"view_name": "api:user-detail",
                              'lookup_field': 'username', 'many': 'True'},
            'users_like': {"view_name": "api:user-detail",
                           'lookup_field': 'username', 'many': 'True'},
            'owner': {"view_name": "api:user-detail",
                      'lookup_field': 'username'}
        }


class InvestmentPortfolioDetailOwnerSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for portfolio owner.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name="api:investmentportfolio-detail")
    securities = SecurityInPortfolioSerializer(many=True, read_only=True)
    trade_securities = TradeHistorySerializerForPortfolioDetail(many=True, read_only=True)
    portfolio_invests = PortfolioInvestHistorySerializer(many=True, read_only=True)

    class Meta:
        model = InvestmentPortfolio
        exclude = [
            'owner',
            'previos_today_cash',
            'previos_percent_profit',
            'previos_year_percent_profit'
        ]
        extra_kwargs = {
            'users_follows': {"view_name": "api:user-detail",
                              'lookup_field': 'username', 'many': 'True'},
            'users_like': {"view_name": "api:user-detail",
                           'lookup_field': 'username', 'many': 'True'},
            'owner': {"view_name": "api:user-detail",
                      'lookup_field': 'username'}
        }


class InvestmentPortfolioListSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for list portfolios.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name="api:investmentportfolio-detail")
    owner_name = serializers.CharField(source="owner")
    owner_id = serializers.IntegerField(source="owner.id")

    class Meta:
        model = InvestmentPortfolio
        fields = ['owner',
                  'owner_name',
                  'owner_id',
                  'url',
                  'title',
                  'percent_profit',
                  'change_percent_profit',
                  'year_percent_profit',
                  'change_year_percent_profit']
        extra_kwargs = {
            'owner': {"view_name": "api:user-detail",
                      'lookup_field': 'username'}
        }


class MyInvestmentPortfolioListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InvestmentPortfolio
        fields = [
            'url',
            'title',
            'invest_cash',
            'today_cash',
            'change_today_cash',
            'percent_profit',
            'change_percent_profit',
            'year_percent_profit',
            'change_year_percent_profit',
        ]
        extra_kwargs = {
            'url': {"view_name": "api:investmentportfolio-detail"}
        }
