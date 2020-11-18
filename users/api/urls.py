from django.urls import path
from .views import AppUserListAdminAccess, AppUserListAppUserAccess, \
    AppUserDetailAppUserAccess

urlpatterns = [
    # admin views
    path(
        'admin/',
        AppUserListAdminAccess.as_view(),
        name='app_user_list_admin_access'),
    path(
        '',
        AppUserListAppUserAccess.as_view(),
        name='app_user_list_app_admin_access'),
    path(
        '<pk>/',
        AppUserDetailAppUserAccess.as_view(),
        name='app_user_detail_app_admin_access')
]
