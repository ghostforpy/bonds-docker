from rest_framework import serializers
from django.urls import reverse
from ..models import BReport
#from bonds.users.api.serializers import UserSerializer
# from moex.api.serializers import SecurityInPortfolioSerializer,\
#    TradeHistorySerializerForPortfolioDetail


class BReportUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = BReport
        exclude = ['created']
        read_only_fields = ['owner', 'filename', 'created']
