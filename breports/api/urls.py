from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import path, include
#from portfolio.api.views import PortfolioViewSet, PortfolioInvestHistoryViewSet
from .views import BReportFileUploadViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('breports', BReportFileUploadViewSet, basename='breports')
# <pk> not metter, allways return user_informer by requset.user

urlpatterns = [
    path('', include(router.urls)),
]
