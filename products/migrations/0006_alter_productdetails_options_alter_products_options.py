# Generated by Django 4.2.1 on 2024-06-26 17:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_productdetails_size'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productdetails',
            options={'ordering': ['product__brand', 'product__product_name'], 'verbose_name_plural': 'Product Details'},
        ),
        migrations.AlterModelOptions(
            name='products',
            options={'ordering': ['brand', 'product_name'], 'verbose_name_plural': 'Products'},
        ),
    ]