# Generated by Django 2.2 on 2021-07-18 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_order_ref_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='stripe_charge_id',
            new_name='stripe_payment_intent',
        ),
    ]
