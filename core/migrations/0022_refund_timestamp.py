# Generated by Django 2.2 on 2021-07-22 10:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20210718_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
