# Generated by Django 5.0.8 on 2024-09-22 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0037_remove_order_coupon_applied'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
