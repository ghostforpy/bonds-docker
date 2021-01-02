# Generated by Django 3.0.7 on 2021-01-02 20:21

from django.db import migrations
from ..models import PortfolioInvestHistory

def refill_cash_in_rub_in_portfolioinvesthistory(apps, schema_editor):
    for i in PortfolioInvestHistory.objects.all():
        if i.currency == 'SUR':
            i.cash_in_rub = i.cash
        i.save(update_fields=['cash_in_rub'],simple_update=True)

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0022_portfolioinvesthistory_cash_in_rub'),
    ]

    operations = [
        migrations.RunPython(refill_cash_in_rub_in_portfolioinvesthistory),
    ]
