# Generated by Django 4.2.1 on 2024-04-30 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutriforce_app', '0006_rename_related_products_products_categories_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
