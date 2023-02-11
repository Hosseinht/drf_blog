from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from blog.models import Category, Post

from .paginations import PostPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import CategorySerializer, PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related("author", "category").all()
    serializer_class = PostSerializer
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["author__email", "status", "category__name"]
    search_fields = ["title", "content"]
    ordering_fields = ["published_at"]
    pagination_class = PostPagination


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
