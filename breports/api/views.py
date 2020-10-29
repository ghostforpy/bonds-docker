from django.core.exceptions import ObjectDoesNotExist
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
#from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from ..models import BReport
from .serializers import BReportUploadSerializer


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
    serializer_class = BReportUploadSerializer
    parser_classes = (MultiPartParser, FormParser,)
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user,
                        filename=self.request.data.get('filename'))
