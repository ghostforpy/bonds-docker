from rest_framework.mixins import (ListModelMixin,
                                   RetrieveModelMixin,
                                   CreateModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny,
                                        SAFE_METHODS,
                                        BasePermission)
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from ..models import PortfolioInvestHistory, InvestmentPortfolio
from .serializers import (InvestmentPortfolioDetailSerializer,
                          InvestmentPortfolioListSerializer,
                          InvestmentPortfolioDetailOwnerSerializer,
                          InvestmentPortfolioCreateSerializer,
                          InvestmentPortfolioUpdateSerializer,
                          MyInvestmentPortfolioListSerializer)


class PageNumberPaginationBy10(PageNumberPagination):
    page_size = 10


class PortfolioIsManual(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.manual


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


class PortfolioViewSet(ListModelMixin,
                       RetrieveModelMixin,
                       UpdateModelMixin,
                       CreateModelMixin,
                       # delete
                       GenericViewSet):
    """
    Viewset for list, retrivie,
    create, update, delete security model.
    Include url 'my-list/ for list user's portfolios.
    Include query_params 'owner' for list portfolios by user
    """
    pagination_class = PageNumberPaginationBy10

    def get_queryset(self):
        queryset = InvestmentPortfolio.objects.all()

        if self.action == 'my_list':
            user = self.request.user
            return queryset.filter(owner=user)
        if self.action == 'list':
            if 'owner' in self.request.query_params:
                q = self.request.query_params.get('owner')
                return queryset.filter(owner__username=q)
        return InvestmentPortfolio.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return InvestmentPortfolioListSerializer
        if self.action == 'my_list':
            return MyInvestmentPortfolioListSerializer
        if self.action == 'create':
            return InvestmentPortfolioCreateSerializer
        if self.action in ['update', 'partial_update']:
            return InvestmentPortfolioUpdateSerializer
        elif self.action == 'retrieve':
            if self.request.user == self.get_object().owner:
                return InvestmentPortfolioDetailOwnerSerializer
            else:
                return InvestmentPortfolioDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """
        Instantiates and returns the list
        of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [AllowAny]
        if self.action in ['my_list', 'create']:
            permission_classes = [IsAuthenticated]
        if self.action in ['update', 'partial_update']:
            permission_classes = [PortfolioIsManual & IsOwnerOrReadOnlyAuthorized]
        else:
            permission_classes = [IsOwnerOrReadOnlyAuthorized]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False,
            url_path='my-list', url_name='my-list')
    def my_list(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

