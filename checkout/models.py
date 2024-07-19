from django.db import models
from django.utils.translation import gettext_lazy as _
from addresses.models import Addresses
from products.models import ProductDetails
from profiles.models import User


class OrderHistory(models.Model):
    """Model for completed orders and all relevant details"""
    class Status(models.TextChoices):
        PEND = 'PEND', _('Pending')
        PROCESS = 'PROC', _('Processing')
        READY = 'RDY', _('Ready to Ship')
        SHIPPED = 'SHP', _('Shipped')
        DELIVERED = 'DLV', _('Delivered')

    order_id = models.AutoField(primary_key=True)
    order_dt = models.DateTimeField(auto_now_add=True)
    billing_addr = models.ForeignKey(Addresses,
                                     related_name='billing_addr',
                                     on_delete=models.SET('0'))
    shipping_addr = models.ForeignKey(Addresses,
                                      related_name='shipping_addr',
                                      on_delete=models.SET('0'))
    order_note = models.TextField(blank=True,
                                  null=True)
    subtotal = models.DecimalField(max_digits=6,
                                   decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=6,
                                        decimal_places=2)
    grand_total = models.DecimalField(max_digits=6,
                                      decimal_places=2)
    purchaser = models.ForeignKey(User,
                                  on_delete=models.SET('0'),
                                  blank=True,
                                  null=True)
    purchaser_email = models.EmailField()
    status = models.CharField(max_length=50,
                              choices=Status.choices,
                              default=Status.PEND)
    tracking_link = models.TextField(blank=True,
                                     null=True)
    stripe_pid = models.CharField(max_length=254)

    class Meta:
        ordering = ['-order_dt', 'status']
        verbose_name_plural = 'Order Histories'

    def __str__(self):
        return f'{self.order_id} | {self.status} | {self.order_dt}'


class Purchases(models.Model):
    """Model for purchased products belonging to orders in OrderHistory model"""
    purchase_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(OrderHistory,
                              on_delete=models.PROTECT)
    product = models.ForeignKey(ProductDetails,
                                on_delete=models.PROTECT)

    quantity = models.IntegerField()

    class Meta:
        ordering = ['-purchase_id', 'product']
        verbose_name_plural = 'Purchases'

    def __str__(self):
        return f'{self.order} | {self.product} | {self.quantity}'
