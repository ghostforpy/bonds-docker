# from rest_framework import status, viewsets
# from django.shortcuts import get_object_or_404
# from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin,\
    RetrieveModelMixin
#    UpdateModelMixin
# from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,\
    AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination
from .serializers import SecurityRetrivieSerializer,\
    SecurityListSerializer
from ..models import Security


class PageNumberPaginationBy5(PageNumberPagination):
    page_size = 5


class SecurityViewSet(ListModelMixin,
                      RetrieveModelMixin,
                      GenericViewSet):
    """
    Viewset for list and retrivie security model.
    """
    queryset = Security.objects.all()
    pagination_class = PageNumberPaginationBy5

    def get_serializer_class(self):
        if self.action == 'list':
            return SecurityListSerializer
        elif self.action == 'retrieve':
            return SecurityRetrivieSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list
        of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
