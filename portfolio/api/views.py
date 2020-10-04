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


class FollowLikePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.request_user_has_permission(request.user)


class PortfolioViewSet(ListModelMixin,
                       RetrieveModelMixin,
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
        elif self.action in ['retrieve', 'follow', 'like']:
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
        if self.action in ['follow', 'like']:
            permission_classes = [FollowLikePermission]
        else:
            permission_classes = [IsOwnerOrReadOnlyAuthorized]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False,
            url_path='my-list', url_name='my-list')
    def my_list(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

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
