# Generated by Django 4.2.1 on 2024-06-26 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='main_cat',
            field=models.CharField(choices=[('SPORTS', 'Sports'), ('HEALTH', 'Health')], default='SPORTS', max_length=50),
            preserve_default=False,
        ),
    ]