# Generated by Django 5.0.8 on 2024-09-01 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_offer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=50),
        ),
    ]
