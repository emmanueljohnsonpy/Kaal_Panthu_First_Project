# Generated by Django 5.0.8 on 2024-09-01 03:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_product_old_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='size',
        ),
    ]
