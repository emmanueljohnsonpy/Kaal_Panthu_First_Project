# Generated by Django 5.0.8 on 2024-09-01 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_product_product_disc_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cat_disc_added',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
