# Generated by Django 5.0.8 on 2024-09-02 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_order_coupon_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='after_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='before_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
