# Generated by Django 4.1 on 2023-12-23 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='vendor_slug',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
