from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Userprofil
from config import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Userprofil.objects.create(user=instance)
