from django.urls import path
from .views import OrganizationListView, OrganizationDetailView

urlpatterns = [
    path('', OrganizationListView.as_view()),
    path('<pk>', OrganizationDetailView.as_view()),
]
