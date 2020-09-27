from rest_framework import serializers
from ..models import InvestmentPortfolio, PortfolioInvestHistory
from bonds.users.api.serializers import UserSerializer


class InvestmentPortfolioDetailSerializer(serializers.HyperlinkedModelSerializer):
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
    url = serializers.HyperlinkedIdentityField(
        view_name="api:investmentportfolio-detail")

    class Meta:
        model = InvestmentPortfolio
        fields = '__all__'
        extra_kwargs = {
            'users_follows': {"view_name": "api:user-detail",
                              'lookup_field': 'username', 'many': 'True'},
            'users_like': {"view_name": "api:user-detail",
                           'lookup_field': 'username', 'many': 'True'},
            'owner': {"view_name": "api:user-detail",
                      'lookup_field': 'username'}
        }


class InvestmentPortfolioListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:investmentportfolio-detail")
    owner_name = serializers.CharField(source="owner")

    class Meta:
        model = InvestmentPortfolio
        fields = ['owner',
                  'owner_name',
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
