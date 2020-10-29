from django.contrib import admin
from .models import BReport
# Register your models here.


@admin.register(BReport)
class BReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'filename', 'created']
    list_filter = ('owner',)
