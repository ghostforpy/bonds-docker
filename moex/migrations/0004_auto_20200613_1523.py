# Generated by Django 3.0.5 on 2020-06-13 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moex', '0003_security_fullname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='fullname',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
