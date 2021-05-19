import datetime

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.settings import CACHE_KEY_GENERATOR
from outlets.models import Outlet, OutletOwner, OutletUser


@receiver(post_save, sender=Outlet)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())


@receiver(post_save, sender=OutletUser)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())


@receiver(post_save, sender=OutletOwner)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())
