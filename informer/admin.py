from django.contrib import admin
from .models import UserInformer
# Register your models here.


@admin.register(UserInformer)
class UserInformerAdmin(admin.ModelAdmin):
    list_display = ['user', 'enable']
    list_filter = ('user', 'enable',)
