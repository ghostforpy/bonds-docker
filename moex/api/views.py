from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
# from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
#    RetrieveModelMixin,\
#    UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
#from rest_framework.permissions import IsAuthenticated, AllowAny
#from rest_framework.decorators import api_view, permission_classes

from .serializers import SecurityRetrivieSerializer,\
    SecurityListSerializer
from ..models import Security


class SecurityViewSet(ListModelMixin, GenericViewSet):
    """
    Viewset for list and retrivie security model.
    """
    #serializer_class = SecuritySerializer
    queryset = Security.objects.all()

    def list(self, request):
        #queryset = Security.objects.all()
        serializer = SecurityListSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        #queryset = Security.objects.all()
        security = get_object_or_404(self.queryset, pk=pk)
        serializer = SecurityRetrivieSerializer(security)
        return Response(serializer.data)
