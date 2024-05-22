# Generated by Django 4.2.1 on 2024-05-22 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutriforce_app', '0013_purchasehistory_shipping_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasehistory',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, default=5, max_digits=6),
            preserve_default=False,
        ),
    ]
