# Generated by Django 2.2 on 2021-08-17 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20210817_2041'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productrate',
            old_name='user_rate',
            new_name='user_rates',
        ),
    ]
