from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT

api_urlpatterns = [
    path('organizations/', include('organizations.api.urls')),
    path('locations/', include('locations.api.urls')),
    path('cameras/', include('cameras.api.urls')),
]

urlpatterns = [
    path('accounts/', include('rest_auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/registration/', include('rest_auth.registration.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
