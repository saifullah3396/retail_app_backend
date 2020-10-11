from django.urls import path
from .views import CameraListView, CameraDetailView

urlpatterns = [
    path('', CameraListView.as_view()),
    path('<pk>', CameraDetailView.as_view()),
]
