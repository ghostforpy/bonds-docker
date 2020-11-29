from django.contrib import admin
from .models import UserInformer
# Register your models here.


class ToogleEnableMixin():
    def toogle_enable(self, request, queryset):
        for obj in queryset:
            if obj.enable:
                obj.enable = False
            else:
                obj.enable = True
            obj.save()

    toogle_enable.short_description = "Отключить/Включить"
    actions = [toogle_enable]


@admin.register(UserInformer)
class UserInformerAdmin(ToogleEnableMixin, admin.ModelAdmin):
    list_display = ['id', 'user', 'enable']
    list_filter = ('user', 'enable',)
