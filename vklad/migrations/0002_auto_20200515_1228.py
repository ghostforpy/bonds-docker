# Generated by Django 3.0.5 on 2020-05-15 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vklad', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vkladinvesthistory',
            name='vklad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vklads', to='vklad.UserVklad'),
        ),
    ]
