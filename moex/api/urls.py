from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import path, include
from moex.api.views import SecurityViewSet


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('securities', SecurityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
