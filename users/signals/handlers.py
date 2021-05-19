import datetime

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.settings import CACHE_KEY_GENERATOR
from users.models import AppUser


@receiver(post_save, sender=AppUser)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())
