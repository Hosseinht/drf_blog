from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination

from drf_yasg.utils import swagger_auto_schema

from blog.models import Category, Post, Like
from blog.selectors import get_posts, get_post
from blog.services import create_post, delete_post, update_post

from .paginations import (
    get_paginated_response,
    get_paginated_response_context,
    PostPagination,
)
from .permissions import IsOwnerOrReadOnly, IsAdminUserOrReadOnly
from .serializers import CategorySerializer, PostSerializer, FilterSerializer

User = get_user_model()


class PostViewSet(ViewSet):
    # queryset = get_posts()
    serializer_class = PostSerializer
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def list(self, request):
        request = self.request
        filter_serializer = FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        try:
            queryset = get_posts(filters=filter_serializer.validated_data)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return get_paginated_response_context(
            pagination_class=PostPagination,
            serializer_class=PostSerializer,
            queryset=queryset,
            request=request,
            view=self,
        )

    # @swagger_auto_schema(request_body=PostSerializer, response=PostSerializer)
    def partial_update(self, request, slug):
        post = Post.objects.get(slug=slug)
        self.check_object_permissions(request, post)
        serializer = self.serializer_class(
            instance=post,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        author = self.request.user
        try:
            update_post(validated_data, author, slug)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        # serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, slug):

        try:
            post = get_post(slug)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug):
        self.check_object_permissions(request, get_post(slug))
        try:
            delete_post(slug)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            post = create_post(
                user=self.request.user,
                category=validated_data.get("category"),
                title=validated_data.get("title"),
                content=validated_data.get("content"),
                image=validated_data.get("image"),
                status=validated_data.get("status"),
                published_at=validated_data.get("published_at"),
            )

        # except Exception as e:
        #     return Response({"detail": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response(
                {"detail": "Slug already exists."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LikeViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, post_slug):
        like = Like.objects.filter(like_post__slug=post_slug, like_user=request.user)
        post = Post.objects.get(slug=post_slug)

        if like.exists():
            like.delete()
            return Response({"message": "Like deleted."})
        else:
            Like.objects.create(like_user=request.user, like_post=post)
            return Response({"message": "Like created."})


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = PostPagination
