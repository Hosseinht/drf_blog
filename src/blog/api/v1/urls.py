from rest_framework.routers import DefaultRouter

from . import views

app_name = "blog-api-v1"

router = DefaultRouter()

router.register("posts", views.PostViewSet, basename="posts")
router.register("categories", views.CategoryViewSet, basename="categories")

urlpatterns = router.urls
