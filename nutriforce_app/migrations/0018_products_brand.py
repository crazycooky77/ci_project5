# Generated by Django 4.2.1 on 2024-05-26 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutriforce_app', '0017_remove_products_size_products_sizes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='brand',
            field=models.CharField(default='DELETED', max_length=50),
            preserve_default=False,
        ),
    ]
