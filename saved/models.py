from django.db import models
from products.models import ProductDetails
from profiles.models import User
from django.utils.translation import gettext_lazy as _


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
        return (f'{self.owner} | {self.list_type} | '
                f'{self.product} | {self.quantity}')
