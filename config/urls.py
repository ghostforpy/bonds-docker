from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from django.http import HttpResponse
from .views import HomePageView
from bonds.users.views import CustomUserSignUp


def favicon(request):
    image_data = open(settings.STATIC_ROOT + "/images/favicons/favicon.ico",
                      "rb").read()
    return HttpResponse(image_data, content_type="image/png")


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/",
         TemplateView.as_view(template_name="pages/about.html"),
         name="about"),
    path("privacy/",
         TemplateView.as_view(template_name="pages/privacy.html"),
         name="privacy"),
    path("faq/",
         TemplateView.as_view(template_name="pages/faq.html"),
         name="faq"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("bonds.users.urls", namespace="users")),
    path("accounts/signup/",\
         CustomUserSignUp.as_view(),\
         name="signup"),
    path("accounts/", include("allauth.urls")),
    path("portfolio/", include("portfolio.urls", namespace="portfolio")),
    path("vklad/", include("vklad.urls", namespace="vklad")),
    path("securities/", include("moex.urls", namespace="moex")),
    path("friends/", include("friends.urls", namespace="friends")),
    path("breports/", include("breports.urls", namespace="breports")),
    path("favicon.ico", favicon, name="favicon"),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
