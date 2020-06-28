from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin, ExportActionMixin
# Register your models here.
from .models import *


class SecurityResource(resources.ModelResource):
    class Meta:
        model = Security
      #  exclude = ('id',)


class RefreshSecurityMixin(ExportActionMixin):

    def refresh_security(self, request, queryset):
        for obj in queryset:
            obj.refresh_price()

    refresh_security.short_description = "Обновить данные"
    actions = ExportActionMixin.actions + [refresh_security]


@admin.register(Security)
class SecurityAdmin(ImportExportMixin,
                    RefreshSecurityMixin,
                    admin.ModelAdmin):
    list_display = ['name', 'security_type', 'emitent',
                    'last_update', 'oldest_date', 'today_price']
    list_filter = ('security_type', 'last_update', 'emitent', 'oldest_date',)
    search_fields = ('name',
                     'code',
                     'shortname',
                     'regnumber',
                     'secid',
                     'isin')
    resource_class = SecurityResource


@admin.register(SecurityHistory)
class SecurityHistoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'price',
                    'percent_prev_date']
    list_filter = ('name', 'date',)
    search_fields = ('name',)


@admin.register(SecurityPortfolios)
class SecurityPortfoliosAdmin(admin.ModelAdmin):
    list_display = ['owner', 'portfolio', 'security', 'count',
                    'today_price']
    list_filter = ('owner', 'portfolio', 'security',)
    search_fields = ('security',)


@admin.register(TradeHistory)
class TradeHistoryAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    list_display = ['owner', 'portfolio', 'security', 'count',
                    'price', 'date', 'buy', 'commission']
    list_filter = ('owner', 'portfolio', 'security', 'date', 'buy',)
    search_fields = ('security',)
