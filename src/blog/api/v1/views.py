from rest_framework.viewsets import ModelViewSet

from blog.models import Category, Post

from .serializers import CategorySerializer, PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related("author", "category").all()
    serializer_class = PostSerializer
    lookup_field = "slug"


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
