# Generated by Django 3.0.5 on 2020-06-26 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moex', '0009_auto_20200622_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='last_update',
            field=models.DateField(blank=True),
        ),
    ]
