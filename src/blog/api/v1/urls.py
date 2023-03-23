from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import views

app_name = "api-v1"

router = DefaultRouter()

router.register("posts", views.PostViewSet, basename="posts")
router.register("categories", views.CategoryViewSet, basename="categories")
# router.register("comments", views.CommentViewSet, basename="comments")

posts_router = routers.NestedDefaultRouter(router, "posts", lookup="post")
posts_router.register("like", views.LikeViewSet, basename="like")
posts_router.register("favorite", views.FavoritePostViewSet, basename="favorite")
posts_router.register("comments", views.CommentViewSet, basename="comments")

urlpatterns = router.urls + posts_router.urls
