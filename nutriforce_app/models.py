from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
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
    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    addr_line_1 = models.CharField(max_length=50)
    addr_line_2 = models.CharField(max_length=50,
                                   null=True,
                                   blank=True)
    addr_line_3 = models.CharField(max_length=50,
                                   null=True,
                                   blank=True)
    city = models.CharField(max_length=50)
    eir_code = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    country = models.CharField(max_length=50,
                               default='Ireland')
    phone_nr = models.IntegerField()
    default_addr = models.BooleanField(default=True)

    class Meta:
        ordering = ['county', 'city']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.county} | {self.city} | {self.eir_code}'


class Products(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    product_pic = CloudinaryField('image')
    price = models.DecimalField(max_digits=6,
                                decimal_places=2)
    size = models.CharField(max_length=50)
    description = models.TextField()
    stock_count = models.IntegerField()
    ingredients = models.TextField()
    active = models.BooleanField(default=True)
    categories = models.TextField(blank=True,
                                  null=True)
    created_ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-active', 'product_name']
        verbose_name_plural = 'Products'

    def __str__(self):
        return f'{self.active} | {self.product_name} | {self.size} | {self.price} | {self.stock_count}'


class PurchaseHistory(models.Model):

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
    order_dt = models.DateTimeField(auto_now_add=True)
    billing_addr = models.ForeignKey(Addresses,
                                     related_name='billing_addr',
                                     on_delete=models.SET('deleted_user'))
    shipping_addr = models.ForeignKey(Addresses,
                                      related_name='shipping_addr',
                                      on_delete=models.SET('deleted_user'))
    payment_type = models.CharField(max_length=50,
                                    choices=PaymentType.choices)
    purchaser = models.ForeignKey(User,
                                  on_delete=models.SET('deleted_user'))
    status = models.CharField(max_length=50,
                              choices=Status.choices,
                              default=Status.PEND)
    tracking_link = models.TextField(blank=True,
                                     null=True)

    class Meta:
        ordering = ['-order_dt', 'status']
        verbose_name_plural = 'Purchase Histories'

    def __str__(self):
        return f'{self.status} | {self.order_dt}'


class Purchases(models.Model):
    purchase_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(PurchaseHistory,
                              on_delete=models.RESTRICT)
    product = models.ForeignKey(Products,
                                on_delete=models.RESTRICT)
    quantity = models.IntegerField()

    class Meta:
        ordering = ['-purchase_id', 'product']
        verbose_name_plural = 'Purchases'

    def __str__(self):
        return f'{self.purchase_id} | {Products.product_name} | {self.quantity}'


class SavedItems(models.Model):

    class ListType(models.TextChoices):
        CART = 'CART', _('Cart')
        WATCH = 'WATCH', _('Watchlist')
        SAVED = 'SAVED', _('Saved List')

    list_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Products,
                                on_delete=models.SET('deleted_product'))
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
