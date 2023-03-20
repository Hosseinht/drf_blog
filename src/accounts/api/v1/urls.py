from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views

app_name = "api-v1"

urlpatterns = [
    path("register/", views.RegisterUserView.as_view(), name="register-user"),
    path(
        "activation/verify/confirm/<token>/",
        views.UserActivationView.as_view(),
        name="verify-user",
    ),
    path(
        "activation/resend/",
        views.ResendActivationLinkView.as_view(),
        name="resend-activation-link",
    ),
    path(
        "change-password/",
        views.ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "reset-password-email/",
        views.PasswordResetEmailView.as_view(),
        name="reset-password-email",
    ),
    path(
        "reset-password-confirm/<uidb64>/<token>/",
        views.PasswordResetTokenValidateView.as_view(),
        name="reset-password-token",
    ),
    path("token/login/", views.TokenLoginView.as_view(), name="login-user"),
    path("token/logout/", views.TokenLogoutView.as_view(), name="logout-user"),
    path("jwt/create/", views.CreateJwtTokenView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    path("profile/", views.ProfileAPIView.as_view(), name="profile"),
]
