# Generated by Django 3.0.5 on 2020-05-14 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_auto_20200514_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmentportfolio',
            name='percent_profit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
