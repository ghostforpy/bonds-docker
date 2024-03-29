# Generated by Django 3.0.7 on 2021-04-27 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moex', '0039_security_issuesize'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='security_type',
            field=models.CharField(choices=[('pif_rshb', 'ОПИФ РСХБ'), ('ppif', 'БПИФ'), ('share', 'Акция'), ('bond', 'Облигация'), ('futures', 'Фьючерс'), ('index', 'Индекс'), ('etf_ppif', 'ETF'), ('depositary_receipt', 'Депозитарная расписка'), ('currency', 'Валюта')], default='bond', max_length=20),
        ),
    ]
