from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from . import views

app_name = "api-v1"

urlpatterns = [
    path("register/", views.RegisterUserAPIView.as_view(), name="register-user"),
    path("token/login/", views.ObtainAuthTokenView.as_view(), name="login-user"),
]
