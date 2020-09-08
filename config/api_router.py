from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from bonds.users.api.views import UserViewSet
from moex.api.views import SecurityViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("securities", SecurityViewSet)

app_name = "api"
urlpatterns = router.urls
