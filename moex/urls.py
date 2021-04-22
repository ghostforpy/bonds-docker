from django.urls import path
from . import views

# create your routs

app_name = 'moex'

urlpatterns = [

    path('search_moex/', views.security_search_moex, name='search_moex'),
    path('buy/<int:id>/', views.security_buy, name='buy'),
    path('delete_history/<int:id>/',
         views.delete_history,
         name='delete_history'),
    path('detail2/<int:id>/', views.security_detail, name='detail_old'),
    path('detail/<int:id>/', views.security_detail_vue, name='detail'),
    path('detail-new/<secid>/', views.new_security_detail, name='new_detail'),
    path('buy-new/<secid>/', views.new_security_buy, name='new_buy'),
    path('add-new/<secid>/', views.add_new_security_for_staff,
         name='add_new_security_for_staff'),
    path('new_security_history/<secid>/',
         views.get_new_security_history, name='get_new_security_history'),
    path('refresh/<int:id>/', views.refresh_security, name='refresh_security'),
    path('follow/<int:id>/', views.security_follow, name='follow'),
    path('sp/<int:id_p>/<int:id_s>/', views.sp, name='sp'),
    path('security_history/<int:id>/',
         views.get_security_history, name='get_security_history'),
    path('old-list/', views.security_list, name='list-old'),
    path('', views.security_list_vue, name='list'),
]
