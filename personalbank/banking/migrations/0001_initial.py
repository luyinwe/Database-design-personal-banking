# Generated by Django 3.1.2 on 2020-11-27 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='account',
            fields=[
                ('account_number', models.CharField(max_length=15, primary_key=True, serialize=False, unique=True)),
                ('balance', models.FloatField(default=0)),
                ('rating', models.CharField(choices=[('1', 'initial'), ('2', 'good'), ('3', 'very good'), ('4', 'excellent'), ('5', 'VIP')], default='1', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='operator',
            fields=[
                ('username', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=100)),
                ('Name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='user',
            fields=[
                ('username', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('Name', models.CharField(max_length=100)),
                ('residential_address', models.CharField(max_length=100)),
                ('ssn', models.CharField(max_length=18)),
            ],
        ),
        migrations.CreateModel(
            name='wire_transfer',
            fields=[
                ('wt_transaction_no', models.CharField(max_length=9, primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('currency_type', models.CharField(max_length=10)),
                ('amount', models.FloatField(default=0)),
                ('state', models.CharField(choices=[('S', 'successful'), ('P', 'pending'), ('F', 'failed')], default='pending', max_length=1)),
                ('payee_name', models.CharField(max_length=100)),
                ('payee_bank_name', models.CharField(max_length=100)),
                ('payee_account_no', models.CharField(max_length=100)),
                ('payee_swift_code', models.CharField(max_length=100)),
                ('account_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.account')),
                ('operator_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.operator')),
            ],
        ),
        migrations.CreateModel(
            name='transaction',
            fields=[
                ('transaction_no', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('transaction_date', models.DateTimeField()),
                ('amount', models.FloatField(default=0)),
                ('purpose', models.CharField(max_length=20)),
                ('payee_account_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payee_account_no', to='banking.account')),
                ('payer_account_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payer_account_no', to='banking.account')),
            ],
        ),
        migrations.CreateModel(
            name='loan',
            fields=[
                ('loan_application_number', models.CharField(max_length=9, primary_key=True, serialize=False)),
                ('amount', models.FloatField(default=0)),
                ('state', models.CharField(choices=[('S', 'successful'), ('P', 'pending'), ('F', 'failed')], default='P', max_length=1)),
                ('due_date', models.DateTimeField()),
                ('account_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.account')),
                ('operator_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.operator')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='operator_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.operator'),
        ),
        migrations.AddField(
            model_name='account',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.user'),
        ),
    ]
