"""
Defines the base url configuration for our application.
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_jwt.views import obtain_jwt_token

from app_organizations.api.urls import urlpatterns as organizations

from .settings import MEDIA_ROOT, MEDIA_URL

api_urlpatterns = [
    path('users/', include([
        path('', include('users.api.urls')),
        path('', include('user_auth.api.urls')),
    ])),
    path('organizations/', include([
        path('', include('app_organizations.api.urls')),
        path('<organization>/', include([
            path('outlets/', include([
                path('', include('outlets.api.urls')),
                path('<outlet>/', include([
                    path('locations/', include([
                        path('', include('locations.api.urls')),
                        # path('floors/<floor>/block/<blocks>', include([
                        #     # path('frames/', include('measurement_frames.api.urls')),
                        #     # path('cameras/', include('cameras.api.urls')),
                        # ]))
                    ]))
                ]))
            ])),
            # path('deepstream_servers/', include('deepstream_servers.api.urls')),
        ])),
    ])),
]

urlpatterns = [
    path('', include('frontend.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_urlpatterns)),
    path('api-token-auth/', obtain_jwt_token),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
