"""
Defines the base url configuration for our application.
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_jwt.views import obtain_jwt_token

from .settings import MEDIA_ROOT, MEDIA_URL

api_urlpatterns = [
    path('organizations/', include('app_organizations.api.urls')),
    path('organizations/<uuid:organization_pk>/', include([
        path('outlets/', include('outlets.api.urls')),
        path('outlets/<uuid:outlet_pk>/', include([
            path('locations/', include('locations.api.urls'))
        ]))
    ])),
    # path('organizations/', include('locations.api.org_locations.urls')),
    # path('locations/', include('locations.api.urls')),
    # path('frames/', include('measurement_frames.api.urls')),
    # path('deepstream_servers/', include('deepstream_servers.api.urls')),
    # path('cameras/', include('cameras.api.urls')),
    path('users/', include('users.api.urls')),
    path('users/', include('user_auth.api.urls')),
    # path('locations/', include('locations.api.user_locations.urls')),
]

urlpatterns = [
    path('', include('frontend.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),
    path('api-token-auth/', obtain_jwt_token),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
