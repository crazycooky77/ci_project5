# Generated by Django 4.2.1 on 2024-06-26 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_productdetails_options_alter_products_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productdetails',
            name='size',
            field=models.IntegerField(),
        ),
    ]
