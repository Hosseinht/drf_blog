from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers


from . import views

app_name = "api-v1"

router = DefaultRouter()

router.register(
    "posts",
    views.PostViewSet,
    basename="posts",
)
router.register("categories", views.CategoryViewSet, basename="categories")

posts_router = routers.NestedDefaultRouter(router, "posts", lookup="post")
posts_router.register(
    "likes",
    views.LikeViewSet,
    basename="likes",
)

urlpatterns = router.urls + posts_router.urls
