# signals.py
from django.dispatch import Signal, receiver
from accounts.models import PromotionRequest
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from rest_framework import serializers


promotion_requested = Signal()

@receiver(promotion_requested)
def handle_promotion_request(sender, user, **kwargs):
    # Create a promotion request entry
    PromotionRequest.objects.create(user=user)


@receiver(pre_save, sender=PromotionRequest)
def check_promotion_request_limit(sender, instance, **kwargs):
    if PromotionRequest.objects.filter(user=instance.user).count() >= 10:
        raise serializers.ValidationError('A user cannot have more than 10 promotion requests.')
