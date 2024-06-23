from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderHistory


@receiver(post_save, sender=OrderHistory)
def update_on_save(sender, instance, created, **kwargs):
    instance.order.update_total()