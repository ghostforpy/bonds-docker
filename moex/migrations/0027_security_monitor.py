# Generated by Django 3.0.5 on 2020-08-06 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moex', '0026_auto_20200729_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='security',
            name='monitor',
            field=models.BooleanField(default=True),
        ),
    ]
