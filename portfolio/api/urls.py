from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import path, include
from portfolio.api.views import PortfolioViewSet


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('portfolios', PortfolioViewSet, basename='investmentportfolio')
# portfolios include 'my-list/' for list portfolios by owner
# portfolios include '{id}/follow/' for follow-unfollow portfolios
# portfolios include '{id}/like/' for like-unlike portfolios

urlpatterns = [
    path('', include(router.urls)),

]
