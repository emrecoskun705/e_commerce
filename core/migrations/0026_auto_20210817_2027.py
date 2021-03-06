# Generated by Django 2.2 on 2021-08-17 17:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0025_auto_20210817_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rate',
            name='product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Product'),
        ),
        migrations.RemoveField(
            model_name='rate',
            name='user',
        ),
        migrations.AddField(
            model_name='rate',
            name='user',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
