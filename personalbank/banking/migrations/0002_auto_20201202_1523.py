# Generated by Django 3.1.2 on 2020-12-02 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
