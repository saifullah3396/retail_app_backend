from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_jwt.views import obtain_jwt_token

from .settings import MEDIA_ROOT, MEDIA_URL

api_urlpatterns = [
    path('organizations/', include('organizations.api.urls')),
    path('locations/', include('locations.api.urls')),
    path('cameras/', include('cameras.api.urls')),
    path('users/', include('users.api.urls')),
    path('user_auth/', include('user_auth.urls')),
]

urlpatterns = [
    path('', include('frontend.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),
    path('api-token-auth/', obtain_jwt_token),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
