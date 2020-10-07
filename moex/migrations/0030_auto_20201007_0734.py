# Generated by Django 3.0.5 on 2020-10-07 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moex', '0029_auto_20200816_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='faceunit',
            field=models.CharField(blank=True, choices=[('SUR', 'РУБ'), ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('CNY', 'CNY')], default='SUR', max_length=20, null=True),
        ),
    ]
