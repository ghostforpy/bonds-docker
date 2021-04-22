# from rest_framework import status, viewsets
# from django.shortcuts import get_object_or_404
# from rest_framework.decorators import action
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models import Prefetch
from django.contrib.auth import get_user_model
from rest_framework.mixins import ListModelMixin,\
    RetrieveModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework import status as response_status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,\
    AllowAny, BasePermission, IsAdminUser
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from .serializers import (SecurityRetrivieSerializer,
                          SecurityListSerializer,
                          TradeHistorySerializer,
                          TradeHistoryCreateSerializer,
                          TradeHistorySerializerForPortfolioDetail,
                          SecurityHistory,
                          NewSecurityListSerializer)
from ..models import Security, TradeHistory, SecurityPortfolios
from ..utils import (get_security_in_db_history_from_moex,
                     search_new_securities_api,
                     add_search_securities_to_cache)
from portfolio.models import InvestmentPortfolio


class IsOwnerOfPortfolio(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        try:
            portfolio_id = request.query_params.get(
                'portfolio') or request.data['portfolio']
        except KeyError:
            return False
        try:
            portfolio = InvestmentPortfolio.objects.get(
                id=portfolio_id, owner=request.user
            )
        except ObjectDoesNotExist:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOfObjectForDestroy(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class PageNumberPaginationBy15(PageNumberPagination):
    page_size = 15


class PageNumberPaginationBy50(PageNumberPagination):
    page_size = 50


class History:
    def __init__(self, date, price):
        self.date = date
        self.price = price


class SecurityViewSet(ListModelMixin,
                      RetrieveModelMixin,
                      GenericViewSet):
    """
    Viewset for list and retrivie security model.
    Include url '{id}/follow/ method-post for follow-unfollow securities.
    Include url 'search-new/?search=query' for search new securities.
    """
    # queryset = Security.objects.all()
    pagination_class = PageNumberPaginationBy15

    def get_queryset(self):
        query = self.request.query_params.get('search') or ''
        queryset = Security.objects.all().order_by('-last_update', '-id')
        if self.action in ['history', 'search-new']:
            return queryset
        if self.action in ['list']:
            return queryset.filter(
                Q(name__icontains=query) |
                Q(code__icontains=query) |
                Q(fullname__icontains=query) |
                Q(regnumber__icontains=query) |
                Q(secid__icontains=query) |
                Q(isin__icontains=query) |
                Q(emitent__icontains=query)
            )
        user = self.request.user
        qs_users = get_user_model().objects.all()
        return queryset.prefetch_related(
            Prefetch('trades',
                     queryset=TradeHistory.objects.filter(owner=user)
                     ),
            Prefetch('portfolios',
                     queryset=SecurityPortfolios.objects.filter(owner=user)
                     ),
            Prefetch('users_follows', queryset=qs_users)
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return SecurityListSerializer
        elif self.action == 'retrieve':
            return SecurityRetrivieSerializer
        elif self.action == 'history':
            return SecurityHistory
        elif self.action == 'search_new':
            return NewSecurityListSerializer
        else:
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

    @action(methods=['post'], detail=True,
            url_path='follow', url_name='follow')
    def follow(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if request.user in instance.users_follows.all():
            instance.users_follows.remove(request.user)
            status = response_status.HTTP_204_NO_CONTENT
        else:
            instance.users_follows.add(request.user)
            status = response_status.HTTP_200_OK
        instance.save()
        return Response(status=status)


    @action(methods=['get'], detail=False,
            url_path='search-new', url_name='search-new')
    def search_new(self, request, *args, **kwargs):
        query = self.request.query_params.get('search')
        result = search_new_securities_api(query)
        add_search_securities_to_cache(result)
        # print(result)
        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True,
            url_path='history', url_name='history')
    def history(self, request, *args, **kwargs):
        instance = self.get_object()
        date_since = request.query_params.get('date_since') or None
        date_until = request.query_params.get(
            'date_until') or datetime.now().date()
        result_history = get_security_in_db_history_from_moex(instance,
                                                              date_since,
                                                              date_until)
        result_history = [
            History(i, result_history[i]) for i in result_history
        ]
        self.pagination_class = PageNumberPaginationBy50
        page = self.paginate_queryset(result_history)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(result_history, many=True)
        return Response(serializer.data)
        return Response(status=response_status.HTTP_200_OK,
                        data=result_history)


class TradeHistoryViewSet(ListModelMixin, GenericViewSet):
    def get_permissions(self):
        if self.action in ['portfolio_list', 'create']:
            permission_classes = [IsOwnerOfPortfolio]
        elif self.action in ['security_list']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['destroy']:
            permission_classes = [IsOwnerOfObjectForDestroy]
        elif self.action == 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'destroy':
            return TradeHistorySerializer
        if self.action == 'create':
            return TradeHistoryCreateSerializer
        if self.action == 'list':
            return TradeHistorySerializerForPortfolioDetail
        if self.action in ['portfolio_list', 'security_list']:
            return TradeHistorySerializer

    def get_queryset(self):
        queryset = TradeHistory.objects.all()
        user = self.request.user
        queryset = queryset.filter(owner=user)
        if self.action in ['portfolio_list']:
            if 'portfolio' in self.request.query_params:
                q = self.request.query_params.get('portfolio')
                return queryset.filter(portfolio__id=q).select_related(
                    'security',
                    'portfolio',
                    'owner'
                )
            else:
                return queryset.none()
        if self.action == 'security_list':
            if 'security' in self.request.query_params:
                q = self.request.query_params.get('security')
                return queryset.filter(security__id=q).select_related(
                    'security',
                    'portfolio',
                    'owner'
                )
            else:
                return queryset.none()
        return queryset  # action = list

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_status = self.perform_destroy(instance)
        if delete_status == 'ok':
            status = response_status.HTTP_204_NO_CONTENT
        else:
            status = response_status.HTTP_400_BAD_REQUEST
        return Response(data=delete_status, status=status)

    def perform_destroy(self, instance):
        return instance.delete()

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_object = self.perform_create(serializer)
        if isinstance(new_object, TradeHistory):
            status = response_status.HTTP_201_CREATED
            response = Response(serializer.data,
                                status=status)
        else:
            status = response_status.HTTP_400_BAD_REQUEST
            response = Response(data=new_object,
                                status=status)
        return response

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    @action(methods=['get'], detail=False,
            url_path='portfolio-list', url_name='portfolio-list')
    def portfolio_list(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    @action(methods=['get'], detail=False,
            url_path='security-list', url_name='security-list')
    def security_list(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)
