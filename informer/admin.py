from django.contrib import admin
from .models import UserInformer
# Register your models here.


@admin.register(UserInformer)
class UserInformerAdmin(admin.ModelAdmin):
    pass
