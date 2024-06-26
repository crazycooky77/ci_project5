from django.contrib.auth.models import AbstractUser, BaseUserManager
from products.models import Products, ProductDetails
from django.db import models
from django.db.models import Sum, F
import uuid
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, password=None, **extra_fields):
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(**extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Addresses(models.Model):

    class Countries(models.TextChoices):
        IE = 'IE', _('Ireland')

    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    addr_line1 = models.CharField(max_length=50)
    addr_line2 = models.CharField(max_length=50,
                                  null=True,
                                  blank=True)
    addr_line3 = models.CharField(max_length=50,
                                  null=True,
                                  blank=True)
    city = models.CharField(max_length=50)
    eir_code = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    country = models.CharField(max_length=50,
                               choices=Countries.choices,
                               default=Countries.IE)
    email = models.EmailField()
    phone_nr = models.IntegerField()
    default_addr = models.BooleanField(default=True)

    class Meta:
        ordering = ['county', 'city']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.county} | {self.city} | {self.eir_code}'


class SavedItems(models.Model):

    class ListType(models.TextChoices):
        CART = 'CART', _('Cart')
        WATCH = 'WATCH', _('Watchlist')
        SAVED = 'SAVED', _('Saved List')

    list_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE)
    product = models.ForeignKey(ProductDetails,
                                on_delete=models.SET('0'))
    quantity = models.IntegerField()
    list_type = models.CharField(max_length=50,
                                 choices=ListType.choices)
    expected_dt = models.DateTimeField(blank=True,
                                       null=True)

    class Meta:
        ordering = ['list_type', 'product']
        verbose_name_plural = 'Saved Items'

    def __str__(self):
        return f'{self.list_type} | {Products.product_name} | {self.quantity}'


class OrderHistory(models.Model):

    class PaymentType(models.TextChoices):
        VISA = 'VISA', _('Visa')
        MC = 'MC', _('mastercard')
        PP = 'PP', _('PayPal')
        GP = 'GP', _('GooglePay')
        AP = 'AP', _('ApplePay')

    class Status(models.TextChoices):
        PEND = 'PEND', _('Pending')
        PROCESS = 'PROC', _('Processing')
        READY = 'RDY', _('Ready to Ship')
        SHIPPED = 'SHP', _('Shipped')
        DELIVERED = 'DLV', _('Delivered')

    order_id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=32,
                                    unique=True,
                                    null=False,
                                    editable=False)
    order_dt = models.DateTimeField(auto_now_add=True)
    billing_addr = models.ForeignKey(Addresses,
                                     related_name='billing_addr',
                                     on_delete=models.SET('0'))
    shipping_addr = models.ForeignKey(Addresses,
                                      related_name='shipping_addr',
                                      on_delete=models.SET('0'))
    shipping_cost = models.DecimalField(max_digits=6,
                                        decimal_places=2)
    total_cost = models.DecimalField(max_digits=6,
                                     decimal_places=2)
    payment_type = models.CharField(max_length=50,
                                    choices=PaymentType.choices)
    purchaser = models.ForeignKey(User,
                                  on_delete=models.SET('0'))
    status = models.CharField(max_length=50,
                              choices=Status.choices,
                              default=Status.PEND)
    tracking_link = models.TextField(blank=True,
                                     null=True)

    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()

    def update_total(self):
        self.total_cost = self.order_purchases.aggregate(
            Sum(F('order_purchases_product_price') *
                F('order_purchases_quantity')))

        if self.total_cost < settings.FREE_SHIPPING_THRESHOLD:
            self.shipping_cost = (self.total_cost *
                                  settings.STANDARD_SHIPPING_PERCENTAGE / 100)
        else:
            self.shipping_cost = 0
        self.save()

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
            super().save(*args, **kwargs)

    class Meta:
        ordering = ['-order_dt', 'status']
        verbose_name_plural = 'Order Histories'

    def __str__(self):
        return f'{self.order_number} | {self.status} | {self.order_dt}'


class Purchases(models.Model):
    purchase_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(OrderHistory,
                              on_delete=models.RESTRICT,
                              related_name='order_purchases')
    product = models.ForeignKey(ProductDetails,
                                on_delete=models.RESTRICT)

    quantity = models.IntegerField()

    class Meta:
        ordering = ['-purchase_id', 'product']
        verbose_name_plural = 'Purchases'

    def __str__(self):
        return f'{self.purchase_id} | {Products.product_name} | {self.quantity}'
