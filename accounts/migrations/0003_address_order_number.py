# Generated by Django 5.0.8 on 2024-09-02 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_account_is_blocked'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='order_number',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
