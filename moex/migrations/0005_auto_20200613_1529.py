# Generated by Django 3.0.5 on 2020-06-13 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moex', '0004_auto_20200613_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='shortname',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
