from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework_jwt.views import obtain_jwt_token
from .settings import MEDIA_URL, MEDIA_ROOT

api_urlpatterns = [
    path('organizations/', include('organizations.api.urls')),
    path('locations/', include('locations.api.urls')),
    path('cameras/', include('cameras.api.urls')),
    path('users/', include('users.api.urls')),
]

urlpatterns = [
    path('accounts/', include('rest_auth.urls')),
    path('accounts/registration/', include('rest_auth.registration.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),
    path('api-token-auth/', obtain_jwt_token),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
