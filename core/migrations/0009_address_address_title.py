# Generated by Django 2.2 on 2021-07-16 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_address_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='address_title',
            field=models.CharField(default='default', max_length=50),
            preserve_default=False,
        ),
    ]
