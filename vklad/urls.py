from django.urls import path
from . import views

# create your routs

app_name = 'vklad'

urlpatterns = [
    path('add_vklad/<int:id>/', views.add_vklad,
         name='add_vklad'),
    path('del_vklad/<int:id>/', views.del_vklad,
         name='del_vklad'),
    path('refresh_vklad/<int:id>/', views.refresh_vklad,
         name='refresh_vklad'),
    path('', views.detail_vklad,
         name='detail_vklad'),
]
