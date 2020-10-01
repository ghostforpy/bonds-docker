from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from bonds.users.api.views import UserViewSet
from moex.api.views import SecurityViewSet
from portfolio.api.views import PortfolioViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("securities", SecurityViewSet)
router.register("portfolios", PortfolioViewSet, basename='investmentportfolio')
# portfolios include 'my-list/' for list portfolios by owner

app_name = "api"

urlpatterns = router.urls
