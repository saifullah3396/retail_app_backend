from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT

api_urlpatterns = [
    path('accounts/', include('rest_registration.api.urls')),
    path('organizations/', include('organizations.api.urls')),
    path('locations/', include('locations.api.urls')),
    path('cameras/', include('cameras.api.urls')),
]

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
