# Generated by Django 2.2 on 2021-08-17 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20210817_2345'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('products', models.ManyToManyField(to='core.Product')),
            ],
        ),
        migrations.DeleteModel(
            name='TrendProduct',
        ),
    ]