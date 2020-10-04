from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from bonds.users.api.views import UserViewSet
from moex.api.views import SecurityViewSet
from portfolio.api.views import PortfolioViewSet
#from portfolio.api import urls
if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)

app_name = "api"
urlpatterns = [
    path('', include('portfolio.api.urls')),
    path('', include('moex.api.urls')),
]
urlpatterns += router.urls
