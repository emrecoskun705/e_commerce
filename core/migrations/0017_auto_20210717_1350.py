# Generated by Django 2.2 on 2021-07-17 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_remove_address_address_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='last_name',
        ),
        migrations.AddField(
            model_name='order',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
