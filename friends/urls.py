from django.urls import path
from . import views

# create your routs

app_name = 'friends'

urlpatterns = [
    path('friends_request_reject/<int:id>/',
         views.friends_request_reject, name='friends_request_reject'),
    path('friends_request_cancel/<int:id>/',
         views.friends_request_cancel, name='friends_request_cancel'),
    path('friends_send_request/<int:id>/',
         views.friends_send_request, name='friends_send_request'),
    path('friends_request_accept/<int:id>/',
         views.friends_request_accept, name='friends_request_accept'),
    path('friends_delete/<int:id>/',
         views.friends_delete, name='friends_delete'),
    path('', views.friends_list, name='list'),
]
