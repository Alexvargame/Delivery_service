from django.db.models.signals import post_save,pre_save

from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def update_calculated_fields(sender, instance, created, **kwargs):
    delivery_cost=instance.get_delivery_cost()
    sender.objects.filter(pk=instance.pk).update(delivery_cost=delivery_cost)

