from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import path, include
from portfolio.api.views import PortfolioViewSet, PortfolioInvestHistoryViewSet


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register('portfolios', PortfolioViewSet, basename='investmentportfolio')
# portfolios include 'my-list/' for list portfolios by owner
# portfolios include '{id}/follow/' for follow-unfollow portfolios methods=post
# portfolios include '{id}/like/' for like-unlike portfolios methods=post

router.register('portfolios-invest-history',
                PortfolioInvestHistoryViewSet,
                basename='portfolio-invest-history')
# /api/portfolios/invest-history/{invest-history} methods=[post, delete]

urlpatterns = [
    path('', include(router.urls)),
]
