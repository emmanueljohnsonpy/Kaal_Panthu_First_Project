# Generated by Django 5.0.8 on 2024-08-29 07:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_wallet'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wallet',
            old_name='wallet_balance',
            new_name='balance',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='date',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='type_of_payment',
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('credit', 'Credit'), ('debit', 'Debit')], max_length=10)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=255)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='orders.wallet')),
            ],
        ),
    ]
