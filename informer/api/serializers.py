from rest_framework import serializers
from django.urls import reverse
from ..models import UserInformer
#from bonds.users.api.serializers import UserSerializer
# from moex.api.serializers import SecurityInPortfolioSerializer,\
#    TradeHistorySerializerForPortfolioDetail


class UserInformerSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserInformer
        fields = ['enable']
