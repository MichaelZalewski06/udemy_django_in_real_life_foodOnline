# Generated by Django 4.1 on 2023-12-23 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_vendor_vendor_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='vendor_slug',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]