# Generated by Django 3.0.5 on 2020-07-05 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moex', '0018_auto_20200704_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='security',
            name='coupondate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='security',
            name='couponfrequency',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='security',
            name='couponpercent',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='security',
            name='couponvalue',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
