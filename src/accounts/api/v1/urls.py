from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

app_name = "api-v1"

urlpatterns = [
    path("register/", views.RegisterUserAPIView.as_view(), name="register-user"),

    path("token/login/", views.ObtainAuthTokenView.as_view(), name="login-user"),
    path("token/logout/", views.DestroyTokenView.as_view(), name="logout-user"),

    path("jwt/create/", views.CustomObtainTokenPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
]
