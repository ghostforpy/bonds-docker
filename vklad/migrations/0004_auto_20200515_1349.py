# Generated by Django 3.0.5 on 2020-05-15 10:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vklad', '0003_auto_20200515_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vkladhistory',
            name='vklad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vklad_historyes', to='vklad.UserVklad'),
        ),
    ]
