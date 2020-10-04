# from rest_framework import status, viewsets
# from django.shortcuts import get_object_or_404
# from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin,\
    RetrieveModelMixin, DestroyModelMixin
from rest_framework import status as response_status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,\
    AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination
from .serializers import SecurityRetrivieSerializer,\
    SecurityListSerializer, TradeHistorySerializer
from ..models import Security, TradeHistory


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


class TradeHistoryViewSet(  # DestroyModelMixin,
        GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'destroy':
            return TradeHistorySerializer

    def get_queryset(self):
        queryset = TradeHistory.objects.all()
        user = self.request.user
        return queryset.filter(owner=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        s = self.perform_destroy(instance)
        if s == 'ok':
            status = response_status.HTTP_204_NO_CONTENT
        else:
            status = response_status.HTTP_400_BAD_REQUEST
        return Response(data=s, status=status)

    def perform_destroy(self, instance):
        return instance.delete()
