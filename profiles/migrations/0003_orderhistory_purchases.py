# Generated by Django 4.2.1 on 2024-06-26 13:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productdetails'),
        ('profiles', '0002_saveditems_addresses'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderHistory',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_dt', models.DateTimeField(auto_now_add=True)),
                ('shipping_cost', models.DecimalField(decimal_places=2, max_digits=6)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=6)),
                ('payment_type', models.CharField(choices=[('VISA', 'Visa'), ('MC', 'mastercard'), ('PP', 'PayPal'), ('GP', 'GooglePay'), ('AP', 'ApplePay')], max_length=50)),
                ('status', models.CharField(choices=[('PEND', 'Pending'), ('PROC', 'Processing'), ('RDY', 'Ready to Ship'), ('SHP', 'Shipped'), ('DLV', 'Delivered')], default='PEND', max_length=50)),
                ('tracking_link', models.TextField(blank=True, null=True)),
                ('billing_addr', models.ForeignKey(on_delete=models.SET('0'), related_name='billing_addr', to='profiles.addresses')),
                ('purchaser', models.ForeignKey(on_delete=models.SET('0'), to=settings.AUTH_USER_MODEL)),
                ('shipping_addr', models.ForeignKey(on_delete=models.SET('0'), related_name='shipping_addr', to='profiles.addresses')),
            ],
            options={
                'verbose_name_plural': 'Order Histories',
                'ordering': ['-order_dt', 'status'],
            },
        ),
        migrations.CreateModel(
            name='Purchases',
            fields=[
                ('purchase_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='order_purchases', to='profiles.orderhistory')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='products.productdetails')),
            ],
            options={
                'verbose_name_plural': 'Purchases',
                'ordering': ['-purchase_id', 'product'],
            },
        ),
    ]
