from django.urls import path, include
from rest_framework import routers
from . import views


# create your routs


#router = routers.DefaultRouter()
#router.register(r'portfolios', views.InvestmentPortfolioViewSet)

app_name = 'portfolio'

urlpatterns = [
    path('sentry-debug/', views.trigger_error, name='trigger_error'),
    path('my_portfolios/', views.my_portfolios, name='my_portfolios'),
    path('create2/', views.portfolio_create, name='create_old'),
    path('create/', views.portfolio_create_vue, name='create'),
    path('add_invest/<int:id>/', views.portfolio_add_invest,
         name='add_invest'),
    path('del_invest/<int:id>/', views.portfolio_del_invest,
         name='del_invest'),
    path('refresh_portfolio/<int:id>/', views.refresh_portfolio,
         name='refresh_portfolio'),
    path('delete_portfolio/<int:id>/', views.delete_portfolio,
         name='delete_portfolio'),
    #path('ranking/', views.portfolio_ranking, name='ranking'),
    path('detail2/<int:id>/', views.portfolio_detail, name='detail'),
    path('detail/<int:id>/', views.portfolio_detail_vue, name='detail_vue'),
    #path('like/', views.portfolio_like, name='like'),
    path('follow/<int:id>/', views.portfolio_follow, name='follow'),
    #    path("api/", include(router.urls)),
    path('', views.portfolio_list, name='list'),
]
