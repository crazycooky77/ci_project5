# Generated by Django 4.2.1 on 2024-06-26 13:02

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Products',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(max_length=50)),
                ('product_name', models.CharField(max_length=50)),
                ('product_pic', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('description', models.TextField()),
                ('categories', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Products',
                'ordering': ['product_name'],
            },
        ),
    ]
