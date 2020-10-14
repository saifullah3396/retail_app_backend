from django.urls import path
from .views import CameraListView, CameraDetailView, CameraFilterListView, \
    CameraFilterDetailView

urlpatterns = [
    path('', CameraListView.as_view()),
    path('<pk>', CameraDetailView.as_view()),
    path('filter/', CameraFilterListView.as_view()),
    path('filter/<pk>', CameraFilterDetailView.as_view()),
]
