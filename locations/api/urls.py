from django.urls import path
from .views import AdminLocationListView, AdminLocationDetailView, \
    AdminFloorListView, AdminFloorDetailView, AdminBlockListView, \
    AdminBlockDetailView, LocationDetailsAppUserAccess

urlpatterns = [
    # admin views
    path('admin/', AdminLocationListView.as_view(), name='locations_admin'),
    path(
        'admin/<pk>',
        AdminLocationDetailView.as_view(),
        name='locations_admin_detail'),
    path('admin/floors/', AdminFloorListView.as_view(), name='floors_admin'),
    path(
        'admin/floors/<pk>',
        AdminFloorDetailView.as_view(),
        name='floors_admin_detail'),
    path('admin/blocks/', AdminBlockListView.as_view(), name='blocks_admin'),
    path(
        'admin/blocks/<pk>',
        AdminBlockDetailView.as_view(),
        name='blocks_admin_detail'),

    path(
        '<pk>',
        LocationDetailsAppUserAccess.as_view(),
        name='locations_detail_app_user_access'),
]
