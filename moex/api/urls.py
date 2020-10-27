from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import path, include
from moex.api.views import SecurityViewSet, TradeHistoryViewSet


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('securities', SecurityViewSet)
router.register('securities-trade-history',
                TradeHistoryViewSet,
                basename='securities-trade-history')
# include delete method
# include create method
# include get method "securities-trade-history/portfolio-list/?portfolio=q
# include get method "securities-trade-history/security-list/?security=q
urlpatterns = [
    path('', include(router.urls)),
]
