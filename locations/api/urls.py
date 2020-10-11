from django.urls import path
from .views import LocationListView, LocationDetailView, FloorListView, \
    FloorDetailView, BlockListView, BlockDetailView

urlpatterns = [
    path('', LocationListView.as_view()),
    path('<pk>', LocationDetailView.as_view()),
    path('floors/', FloorListView.as_view()),
    path('floors/<pk>', FloorDetailView.as_view()),
    path('blocks/', BlockListView.as_view()),
    path('blocks/<pk>', BlockDetailView.as_view()),
]
