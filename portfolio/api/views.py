from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from django.contrib.auth import get_user_model
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
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from breports.broker_parser.classes import FileNotSupported
from breports.scripts import init_broker_report
from moex.models import SecurityPortfolios, TradeHistory
from ..models import PortfolioInvestHistory, InvestmentPortfolio
from .serializers import (InvestmentPortfolioDetailSerializer,
                          InvestmentPortfolioListSerializer,
                          InvestmentPortfolioDetailOwnerSerializer,
                          InvestmentPortfolioCreateSerializer,
                          InvestmentPortfolioCreateByBreportSerializer,
                          ManualInvestmentPortfolioUpdateSerializer,
                          AllowInvestmentPortfolioUpdateSerializer,
                          MyInvestmentPortfolioListSerializer,
                          PortfolioInvestHistoryCreateSerializer,
                          UpdatedInvestmentPortfolioSerializer)
from .scripts import create_portfolio_by_broker_report


class PageNumberPaginationBy10(PageNumberPagination):
    page_size = 10


class IsOwnerOrReadOnlyAuthorized(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # # Instance must have an attribute named `owner`.
        if obj.owner == request.user:
            return True

        if request.method in SAFE_METHODS:
            return obj.request_user_has_permission(request.user)
        return False


class FollowLikePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.request_user_has_permission(request.user)


class IsOwnerOfPortfolioObject(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # # Instance must have an attribute named `owner`.
        if request.user == obj.owner:
            return True
        return False


class IsOwnerOfPortfolioInvestObject(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # # Instance must have an attribute named `owner`.
        if request.user == obj.portfolio.owner:
            return True
        return False


class PortfolioViewSet(ListModelMixin,
                       #                      RetrieveModelMixin,
                       UpdateModelMixin,
                       CreateModelMixin,
                       DestroyModelMixin,
                       GenericViewSet):
    """
    Viewset for list, retrivie,
    create, update, delete portfolio model.
    Include url 'my-list/ for list user's portfolios.
    Include query_params 'owner' for list portfolios by user
    Include url '{id}/follow/ method-post for follow-unfollow portfolios.
    Include url '{id}/like/ method-post for like-unlike portfolios.
    Include url 'create-by-breport/ method-post for create portfolios
    by broker reports.
    """
    pagination_class = PageNumberPaginationBy10

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class(*args, **kwargs)
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        queryset = InvestmentPortfolio.objects.select_related('owner').all()
        if self.action == 'retrieve':
            qs_security = SecurityPortfolios.objects.all().prefetch_related(
                'security')
            qs_trade = TradeHistory.objects.all().prefetch_related('security')
            qs_invests = PortfolioInvestHistory.objects.all()
            qs_users = get_user_model().objects.all()
            return queryset.prefetch_related(
                Prefetch('securities', queryset=qs_security),
                Prefetch('trade_securities', queryset=qs_trade),
                Prefetch('portfolio_invests', queryset=qs_invests),
                Prefetch('portfolio_invests__security'),
                Prefetch('users_follows', queryset=qs_users),
                Prefetch('users_like', queryset=qs_users)
            )
        if self.action == 'my_list':
            user = self.request.user
            return queryset.filter(owner=user)
        if self.action == 'list':
            if 'owner' in self.request.query_params:
                q = self.request.query_params.get('owner')
                return queryset.filter(owner__username=q)
        return queryset

    def get_serializer_class(self, instance=None, *args, **kwargs):
        if self.action == 'list':
            return InvestmentPortfolioListSerializer
        if self.action == 'my_list':
            return MyInvestmentPortfolioListSerializer
        if self.action == 'create':
            return InvestmentPortfolioCreateSerializer
        if self.action == 'create_by_breport':
            return InvestmentPortfolioCreateByBreportSerializer
        if self.action in ['get_updated_portfolio']:
            return UpdatedInvestmentPortfolioSerializer
        if self.action in ['update', 'partial_update']:
            try:
                if instance.manual:
                    return ManualInvestmentPortfolioUpdateSerializer
                else:
                    return AllowInvestmentPortfolioUpdateSerializer
            except AttributeError:
                return AllowInvestmentPortfolioUpdateSerializer
        elif self.action in ['retrieve', 'follow', 'like']:
            if self.request.user == instance.owner:
                return InvestmentPortfolioDetailOwnerSerializer
            else:
                return InvestmentPortfolioDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        if 'today_cash' in self.request.data:
            instance.refresh_portfolio()

    def get_permissions(self):
        """
        Instantiates and returns the list
        of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [AllowAny]
        elif self.action in ['my_list', 'create', 'create_by_breport']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsOwnerOfPortfolioObject]
            #permission_classes = [IsOwnerOrReadOnlyAuthorized]
        elif self.action in ['follow', 'like']:
            permission_classes = [FollowLikePermission]
        elif self.action in ['get_updated_portfolio']:
            permission_classes = [IsOwnerOfPortfolioObject]
        else:
            permission_classes = [IsOwnerOrReadOnlyAuthorized]
        return [permission() for permission in permission_classes]

    @action(methods=['post'], detail=False,
            url_path='create-by-breport', url_name='create-by-breport')
    def create_by_breport(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = None
        if 'filename' in serializer.validated_data:
            # если файл передан на сервер для создания портфеля
            # на его основе
            path_to_file, fs = serializer.save_fs()
            serializer.validated_data.pop('filename')
            serializer.validated_data['owner'] = request.user
            try:
                new_portfolio = serializer.create(serializer.validated_data)
                br = init_broker_report(
                    path_to_file
                )
                d = create_portfolio_by_broker_report(new_portfolio,
                                                      br)
                # функция парсинга брокерского отчета,
                # и записи историй покупок, пополнений и др.
                status = response_status.HTTP_201_CREATED
                data = InvestmentPortfolioCreateSerializer(
                    new_portfolio,
                    context={'request': request}
                ).data
            except FileNotSupported:
                status = response_status.HTTP_400_BAD_REQUEST
            finally:
                fs.delete(path_to_file)
        else:
            status = response_status.HTTP_400_BAD_REQUEST
        return Response(data=data, status=status)

    @action(methods=['get'], detail=False,
            url_path='my-list', url_name='my-list')
    def my_list(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    @action(methods=['get'],
            detail=True,
            url_path='get-updated-portfolio',
            url_name='get-updated-portfolio')
    def get_updated_portfolio(self, request, *args, **kwargs):
        return self.retrieve(self, request, *args, **kwargs)

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

    @action(methods=['post'], detail=True,
            url_path='like', url_name='like')
    def like(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if request.user in instance.users_like.all():
            instance.users_like.remove(request.user)
            status = response_status.HTTP_204_NO_CONTENT
        else:
            instance.users_like.add(request.user)
            status = response_status.HTTP_200_OK
        instance.save()
        return Response(status=status)


class PortfolioInvestHistoryViewSet(CreateModelMixin,
                                    DestroyModelMixin,
                                    GenericViewSet):
    serializer_class = PortfolioInvestHistoryCreateSerializer
    permission_classes = [IsOwnerOfPortfolioInvestObject]

    def get_queryset(self):
        qs_security = SecurityPortfolios.objects.all().prefetch_related(
            'security')
        queryset = PortfolioInvestHistory.objects.select_related(
            'portfolio'
        ).select_related(
            'portfolio__owner'
        ).select_related(
            'security'
        ).prefetch_related(
            Prefetch('portfolio__securities', queryset=qs_security)
        ).filter(
            portfolio__owner=self.request.user
        )
        return queryset
