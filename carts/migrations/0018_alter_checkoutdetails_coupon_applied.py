# Generated by Django 5.0.8 on 2024-09-17 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0017_alter_checkoutdetails_coupon_applied'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutdetails',
            name='coupon_applied',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
