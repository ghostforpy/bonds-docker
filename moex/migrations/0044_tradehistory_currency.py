# Generated by Django 3.0.7 on 2021-11-24 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moex', '0043_securityportfolios_custom_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradehistory',
            name='currency',
            field=models.CharField(blank=True, choices=[('SUR', 'РУБ'), ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('CNY', 'CNY')], default='SUR', max_length=20, null=True),
        ),
    ]
