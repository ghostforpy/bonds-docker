# Generated by Django 3.0.5 on 2020-09-08 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='accept_private_policy',
            field=models.BooleanField(default=False, verbose_name='Согласие с политикой конфиденциальности'),
        ),
    ]
