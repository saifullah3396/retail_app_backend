from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('organizations/api/', include('organizations.api.urls')),
    path('locations/api/', include('locations.api.urls')),
    path('cameras/api/', include('cameras.api.urls')),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
