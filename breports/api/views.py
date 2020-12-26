from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from rest_framework.mixins import (ListModelMixin,
                                   RetrieveModelMixin,
                                   CreateModelMixin,
                                   UpdateModelMixin,
                                   DestroyModelMixin)
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny,
                                        SAFE_METHODS,
                                        BasePermission)
from rest_framework import status as response_status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.decorators import action
from ..models import BReport
from .serializers import (BReportUploadSerializer,
                          IncomeCertificateSerializer,
                          SimpleBReportUploadSerializer,
                          NonZeroSecuritySerializer,
                          InvestsOperationSerializer)
from ..broker_parser.classes import FileNotSupported
from ..scripts import *


class IsOwner(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False


class BReportFileUploadViewSet(CreateModelMixin,
                               GenericViewSet):

    queryset = BReport.objects.all()
    parser_classes = (MultiPartParser, FormParser,)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['year_profit']:
            return SimpleBReportUploadSerializer
        if self.action in ['income_certificate']:
            return IncomeCertificateSerializer
        return BReportUploadSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user,
                        filename=self.request.data.get('filename'))

    @action(methods=['post'], detail=False,
            url_path='year-profit', url_name='year-profit')
    def year_profit(self, request, *args, **kwargs):
        """
        Ручка для получения данных о среднегодовой доходности.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        path_to_file, fs = serializer.save()
        data = None
        try:
            br = init_broker_report(
                path_to_file
            )
            data = calc_year_profit(br)

            status = response_status.HTTP_200_OK
        except FileNotSupported:
            status = response_status.HTTP_400_BAD_REQUEST
        finally:
            fs.delete(path_to_file)
        return Response(status=status, data=data)

    @action(methods=['post'], detail=False,
            url_path='income-certificate', url_name='income-certificate')
    def income_certificate(self, request, *args, **kwargs):
        """
        Ручка для получения данных для заполнения
        справки о доходах.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        path_to_file, fs = serializer.save()
        to_date = serializer.validated_data['to_date']
        since_date = serializer.validated_data['since_date']
        data = None
        try:
            br = init_broker_report(
                path_to_file
            )
            data = income_certificate(br, since_date, to_date)
            status = response_status.HTTP_200_OK
        except FileNotSupported:
            status = response_status.HTTP_400_BAD_REQUEST
        finally:
            fs.delete(path_to_file)
        return Response(status=status, data=data)

        data = None
        try:
            br = init_broker_report(
                path_to_file
            )
            data = income_certificate(br)
            status = response_status.HTTP_200_OK
        except FileNotSupported:
            status = response_status.HTTP_400_BAD_REQUEST
        finally:
            fs.delete(path_to_file)
        return Response(status=status, data=data)
