from rest_framework.mixins import ListModelMixin,\
    RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated,\
    AllowAny, SAFE_METHODS, BasePermission
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination
from ..models import PortfolioInvestHistory, InvestmentPortfolio
from .serializers import InvestmentPortfolioDetailSerializer,\
    InvestmentPortfolioListSerializer, InvestmentPortfolioDetailOwnerSerializer


class PageNumberPaginationBy10(PageNumberPagination):
    page_size = 10


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return obj.request_user_has_permission(request.user)

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class PortfolioViewSet(ListModelMixin,
                       RetrieveModelMixin,
                       GenericViewSet):
    """
    Viewset for list and retrivie security model.
    """
    queryset = InvestmentPortfolio.objects.all()
    pagination_class = PageNumberPaginationBy10

    def get_serializer_class(self):
        if self.action == 'list':
            return InvestmentPortfolioListSerializer
        elif self.action == 'retrieve':
            if self.request.user == self.get_object().owner:
                return InvestmentPortfolioDetailOwnerSerializer
            else:
                return InvestmentPortfolioDetailSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list
        of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]
