# Generated by Django 4.2.1 on 2024-07-01 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0014_alter_addresses_phone_nr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addresses',
            name='phone_nr',
            field=models.IntegerField(),
        ),
    ]
