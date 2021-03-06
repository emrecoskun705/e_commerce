# Generated by Django 2.2 on 2021-08-17 17:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0026_auto_20210817_2027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rate',
            name='product',
        ),
        migrations.RemoveField(
            model_name='rate',
            name='user',
        ),
        migrations.AddField(
            model_name='rate',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ProductRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
                ('user_rate', models.ManyToManyField(to='core.Rate')),
            ],
        ),
    ]
