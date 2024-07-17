from django.db import models
from profiles.models import User
from django.utils.translation import gettext_lazy as _


class Addresses(models.Model):

    class Countries(models.TextChoices):
        IE = 'IE', _('Ireland')

    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
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
    phone_nr = models.CharField(max_length=50)
    default_addr = models.BooleanField(default=True)

    class Meta:
        ordering = ['county', 'city']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.county} | {self.city} | {self.eir_code}'
