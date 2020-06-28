from django.contrib import admin
from .models import UserVklad, VkladHistory, VkladInvestHistory
from import_export.admin import ImportExportMixin, ExportActionMixin
# Register your models here.


@admin.register(UserVklad)
class InvestmentPortfolioAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    list_display = ['owner', 'percent_profit',
                    'year_percent_profit', 'created']
    list_filter = ('owner', 'year_percent_profit', 'percent_profit',)
    search_fields = ('title',)


@admin.register(VkladInvestHistory)
class PortfolioInvestHistoryAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    list_display = ['vklad', 'date', 'cash',
                    'popolnenie']
    list_filter = ('vklad',)
    search_fields = ('vklad',)


@admin.register(VkladHistory)
class PortfolioHistoryAdmin(admin.ModelAdmin):
    list_display = ['vklad', 'date', 'percent_profit',
                    'year_percent_profit']
    list_filter = ('vklad', 'percent_profit', 'year_percent_profit')
    search_fields = ('vklad',)
