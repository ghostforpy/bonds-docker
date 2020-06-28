from django.contrib import admin
from import_export.admin import ExportActionMixin, ImportExportMixin
# Register your models here.

from .models import InvestmentPortfolio, PortfolioInvestHistory,\
    PortfolioHistory


@admin.register(InvestmentPortfolio)
class InvestmentPortfolioAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    list_display = ['owner', 'title', 'percent_profit',
                    'year_percent_profit', 'created']
    list_filter = ('owner', 'year_percent_profit', 'percent_profit',)
    search_fields = ('title',)


@admin.register(PortfolioInvestHistory)
class PortfolioInvestHistoryAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    list_display = ['portfolio', 'date', 'cash',
                    'action']
    list_filter = ('portfolio',)
    search_fields = ('portfolio',)


@admin.register(PortfolioHistory)
class PortfolioHistoryAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ['portfolio', 'date', 'percent_profit',
                    'year_percent_profit']
    list_filter = ('portfolio', 'percent_profit', 'year_percent_profit')
    search_fields = ('portfolio',)
