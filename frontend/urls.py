"""
Defines the main url to point to our frontend application view.
"""

from django.urls import path

from .views import FrontendAppView

urlpatterns = [
    path('', FrontendAppView.as_view()),
]
