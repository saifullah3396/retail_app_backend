"""
Defines custom django database fields that are used in our application.
"""
from django_extensions.db.fields import AutoSlugField, UniqueFieldMixin


class CustomUniqueFieldMixin(UniqueFieldMixin):
    """
    Changes the custom unique field so that it takes soft-deleted objects into
    account while trying to generate a slug id
    """

    def get_queryset(self, model_cls, slug_field):
        for field, model in self._get_fields(model_cls):
            if model and field == slug_field:
                return model._default_manager.all_with_deleted()
        return model_cls._default_manager.all_with_deleted()


class CustomAutoSlugField(CustomUniqueFieldMixin, AutoSlugField):
    pass
