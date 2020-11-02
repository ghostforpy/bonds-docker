from django.urls import path
from . import views

# create your routs

app_name = 'breports'

urlpatterns = [
    path('', views.main, name='main'),
]
