from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.translation import gettext_lazy as _


class Products(models.Model):

    class MainCategory(models.TextChoices):
        SPORTS = 'SPORTS', _('Sports')
        HEALTH = 'HEALTH', _('Health')

    product_id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=50)
    product_name = models.CharField(max_length=50)
    product_pic = CloudinaryField('image')
    description = models.TextField()
    main_cat = models.CharField(max_length=50,
                                choices=MainCategory.choices)
    categories = models.TextField(blank=True,
                                  null=True)

    class Meta:
        ordering = ['product_name']
        verbose_name_plural = 'Products'

    def __str__(self):
        return f'{self.product_id} | {self.brand} | {self.product_name}'


class ProductDetails(models.Model):
    product = models.ForeignKey(Products,
                                on_delete=models.CASCADE)
    on_sale = models.BooleanField(default=False)
    size = models.DecimalField(max_digits=6,
                               decimal_places=2)
    size_unit = models.CharField(max_length=50)
    flavour = models.CharField(max_length=600,
                               blank=True,
                               null=True)
    price = models.DecimalField(max_digits=6,
                                decimal_places=2)
    stock_count = models.IntegerField()
    ingredients = models.TextField()
    active = models.BooleanField(default=True)
    created_ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['product__product_id']
        verbose_name_plural = 'Product Details'

    def __str__(self):
        return (f'{self.pk} | {self.active} | {self.product} | ' +
                f'{self.size} {self.size_unit}'
                f' | {self.flavour} | {self.price} | {self.stock_count}')
