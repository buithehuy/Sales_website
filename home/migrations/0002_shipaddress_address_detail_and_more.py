# Generated by Django 4.2.13 on 2024-05-23 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipaddress',
            name='address_detail',
            field=models.CharField(default='no', max_length=100),
        ),
        migrations.AddField(
            model_name='shipaddress',
            name='address_detail2',
            field=models.CharField(default='no', max_length=100),
        ),
        migrations.AddField(
            model_name='shipaddress',
            name='city',
            field=models.CharField(default='no', max_length=100),
        ),
        migrations.AddField(
            model_name='shipaddress',
            name='district',
            field=models.CharField(default='no', max_length=100),
        ),
        migrations.AddField(
            model_name='shipaddress',
            name='xa',
            field=models.CharField(default='no', max_length=100),
        ),
    ]