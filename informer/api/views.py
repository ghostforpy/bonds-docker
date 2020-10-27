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
#from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from ..models import UserInformer
from .serializers import UserInformerSerializer


class IsOwner(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False


class InformerViewSet(RetrieveModelMixin,
                      UpdateModelMixin,
                      GenericViewSet):
    """
    Viewset for retrivie, update informer model.
    """
    queryset = UserInformer.objects.all()
    serializer_class = UserInformerSerializer
    permission_classes = [IsOwner]

    def get_object(self):
        queryset = self.get_queryset()
        user = self.request.user
        obj = generics.get_object_or_404(queryset, user=user)
        return obj
