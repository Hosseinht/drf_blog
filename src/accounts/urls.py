from django.urls import include, path

app_name = "accounts"

urlpatterns = [
    path("", include("accounts.api.v1.urls")),
]
