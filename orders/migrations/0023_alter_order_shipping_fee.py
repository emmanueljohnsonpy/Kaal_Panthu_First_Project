# Generated by Django 5.0.8 on 2024-09-04 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_alter_order_shipping_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_fee',
            field=models.DecimalField(decimal_places=2, default=70, max_digits=10, null=True),
        ),
    ]
