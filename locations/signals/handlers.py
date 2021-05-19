import datetime

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.settings import CACHE_KEY_GENERATOR
from locations.models import Block, Floor, OrganizationLocation, UserLocation


@receiver(post_save, sender=UserLocation)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())


@receiver(post_save, sender=OrganizationLocation)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())


@receiver(post_save, sender=Floor)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())


@receiver(post_save, sender=Block)
def change_api_updated_at(sender, **kwargs):
    cache.set(CACHE_KEY_GENERATOR(sender), datetime.datetime.utcnow())
