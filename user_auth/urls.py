from django.conf.urls import url
from django.urls import include, path, re_path

from .views import VerifyEmailView, django_rest_auth_null

urlpatterns = [
    path('', include('rest_auth.urls')),
    path('registration/', include('rest_auth.registration.urls')),
    path('registration/verify-email/',
         VerifyEmailView.as_view(), name='verify_email'),
    path('registration/verify-email/<str:key>/',
         VerifyEmailView.as_view(), name='verify_email'),
    path('user', django_rest_auth_null, name='rest_user_details'),
    path('rest-auth/registration/account-email-verification-sent/',
         django_rest_auth_null, name='account_email_verification_sent'),
    path('password-reset/confirm/<str:uidb64>)/<str:token>/',
         django_rest_auth_null, name='password_reset_confirm')
]
