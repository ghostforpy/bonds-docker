# Generated by Django 3.0.5 on 2020-05-14 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0004_auto_20200514_2012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investmentportfolio',
            name='total_likes',
            field=models.PositiveIntegerField(blank=True, db_index=True, default=0),
        ),
    ]
