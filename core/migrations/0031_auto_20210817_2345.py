# Generated by Django 2.2 on 2021-08-17 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_favouriteproduct'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trendproduct',
            name='products',
        ),
        migrations.AddField(
            model_name='trendproduct',
            name='products',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.Product'),
        ),
    ]
