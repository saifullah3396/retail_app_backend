from django.urls import path
from .views import OrganizationListView, OrganizationDetailView
from .views import SubOrganizationListView, SubOrganizationDetailView


urlpatterns = [
    path('', OrganizationListView.as_view()),
    path('<pk>', OrganizationDetailView.as_view()),
    path('sub/', SubOrganizationListView.as_view()),
    path('sub/<pk>', SubOrganizationDetailView.as_view()),
]
