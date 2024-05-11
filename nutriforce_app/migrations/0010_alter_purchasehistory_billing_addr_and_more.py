# Generated by Django 4.2.1 on 2024-05-11 12:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutriforce_app', '0009_alter_addresses_options_alter_products_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasehistory',
            name='billing_addr',
            field=models.ForeignKey(on_delete=models.SET('0000'), related_name='billing_addr', to='nutriforce_app.addresses'),
        ),
        migrations.AlterField(
            model_name='purchasehistory',
            name='purchaser',
            field=models.ForeignKey(on_delete=models.SET('0000'), to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchasehistory',
            name='shipping_addr',
            field=models.ForeignKey(on_delete=models.SET('0000'), related_name='shipping_addr', to='nutriforce_app.addresses'),
        ),
        migrations.AlterField(
            model_name='saveditems',
            name='product',
            field=models.ForeignKey(on_delete=models.SET('0000'), to='nutriforce_app.products'),
        ),
    ]