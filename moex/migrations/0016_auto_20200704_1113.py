# Generated by Django 3.0.5 on 2020-07-04 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moex', '0015_auto_20200704_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='code',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='security',
            name='fullname',
            field=models.CharField(blank=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='security',
            name='isin',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='security',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='security',
            name='regnumber',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='security',
            name='secid',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='security',
            name='shortname',
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
    ]
