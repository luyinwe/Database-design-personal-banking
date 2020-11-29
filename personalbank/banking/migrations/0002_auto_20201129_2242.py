# Generated by Django 3.1.2 on 2020-11-29 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='rating',
            field=models.CharField(choices=[('initial', 'initial'), ('good', 'good'), ('very good', 'very good'), ('excellent', 'excellent'), ('VIP', 'VIP')], default='initial', max_length=100),
        ),
        migrations.AlterField(
            model_name='account',
            name='state',
            field=models.CharField(choices=[('successful', 'successful'), ('pending', 'pending'), ('failed', 'failed')], default='pending', max_length=100),
        ),
        migrations.AlterField(
            model_name='loan',
            name='state',
            field=models.CharField(choices=[('successful', 'successful'), ('pending', 'pending'), ('failed', 'failed')], default='pending', max_length=100),
        ),
        migrations.AlterField(
            model_name='wire_transfer',
            name='state',
            field=models.CharField(choices=[('successful', 'successful'), ('pending', 'pending'), ('failed', 'failed')], default='pending', max_length=100),
        ),
    ]