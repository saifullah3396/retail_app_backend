from rest_framework import filters


class HasLocationAuthorizationFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_staff:
            return queryset
        return queryset.filter(id__in=request.user.authorized_locations.all())
