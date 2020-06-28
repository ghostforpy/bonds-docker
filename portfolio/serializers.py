from .models import InvestmentPortfolio
from rest_framework import serializers


class InvestmentPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentPortfolio
        #fields = '__all__'
        fields = ['id', 'ostatok']
