# Generated by Django 3.0.5 on 2020-10-07 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0019_auto_20200821_2311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolioinvesthistory',
            name='action',
            field=models.CharField(choices=[('vp', 'Пополнение'), ('pv', 'Снятие'), ('tp', 'Доход'), ('bc', 'Комиссия брокера'), ('br', 'Частичное погашение облигаций'), ('tax', 'Налог на доход')], default='vklad_to_portfolio', max_length=20),
        ),
    ]