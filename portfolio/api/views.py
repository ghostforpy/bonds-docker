from rest_framework.mixins import (ListModelMixin,
                                   RetrieveModelMixin,
                                   CreateModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny,
                                        SAFE_METHODS,
                                        BasePermission)
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination
from ..models import PortfolioInvestHistory, InvestmentPortfolio
from .serializers import (InvestmentPortfolioDetailSerializer,
                          InvestmentPortfolioListSerializer,
                          InvestmentPortfolioDetailOwnerSerializer,
                          InvestmentPortfolioCreateSerializer,
                          InvestmentPortfolioUpdateSerializer)


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
                       GenericViewSet):
    """
    Viewset for list and retrivie security model.
    """
    queryset = InvestmentPortfolio.objects.all()
    pagination_class = PageNumberPaginationBy10

    def get_serializer_class(self):
        # print(self.action)
        if self.action == 'list':
            return InvestmentPortfolioListSerializer
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
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        if self.action in ['update', 'partial_update']:
            permission_classes = [PortfolioIsManual & IsOwnerOrReadOnlyAuthorized]
        else:
            permission_classes = [IsOwnerOrReadOnlyAuthorized]
        return [permission() for permission in permission_classes]
