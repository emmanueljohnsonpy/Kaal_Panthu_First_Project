# Generated by Django 5.0.8 on 2024-09-04 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_alter_ordereditems_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_fee',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
