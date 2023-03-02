from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import get_list_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model

from blog.models import Category, Post
from blog.selectors import get_posts, get_post

from .paginations import PostPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import CategorySerializer, PostSerializer
from ...services import create_post

User = get_user_model()


class PostViewSet(ModelViewSet):
    # queryset = Post.objects.select_related("author", "category").all()
    queryset = get_posts()
    serializer_class = PostSerializer
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["author__email", "status", "category__name"]
    search_fields = ["title", "content"]
    ordering_fields = ["published_at"]
    pagination_class = PostPagination

    # def get_queryset(self):
    #
    #     request = self.request
    #     if self.action in ["update", "destroy", "retrieve"]:
    #         slug = self.kwargs["slug"]
    #
    #         return get_post(slug)
    #     else:
    #
    #         return get_posts(request)

    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            post = create_post(validated_data, user=self.request.user)

        # except Exception as e:
        #     return Response(
        #         {"detail": f"{e}"}, status=status.HTTP_400_BAD_REQUEST
        #     )
        except IntegrityError:
            return Response(
                {"detail": "Slug already exists."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
