from django.urls import path
from . import views

# create your routs

app_name = 'moex'

urlpatterns = [
    # path('add_invest/<int:id>/', views.portfolio_add_invest,
    #     name='add_invest'),
    # path('del_invest/<int:id>/', views.portfolio_del_invest,
    #     name='del_invest'),
    # path('refresh_portfolio/<int:id>/', views.refresh_portfolio,
    #     name='refresh_portfolio'),
    # path('delete_portfolio/<int:id>/', views.delete_portfolio,
    #     name='delete_portfolio'),
    path('search_moex/', views.security_search_moex, name='search_moex'),
    path('buy/<int:id>/', views.security_buy, name='buy'),
    path('delete_history/<int:id>/',
         views.delete_history,
         name='delete_history'),
    path('sell/<int:id>/', views.security_sell, name='sell'),
    path('detail/<int:id>/', views.security_detail, name='detail'),
    path('refresh/<int:id>/', views.refresh_security, name='refresh_security'),
    path('sp/<int:id_p>/<int:id_s>/', views.sp, name='sp'),
    path('security_history/<int:id>/',
         views.get_security_history, name='get_security_history'),
    path('', views.security_list, name='list'),
]
