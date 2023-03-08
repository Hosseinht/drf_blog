from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, pagination, serializers
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination

from drf_yasg.utils import swagger_auto_schema

from blog.models import Category, Post
from blog.selectors import get_posts, get_post
from blog.services import create_post, delete_post, update_post

from .paginations import (
    PostPagination,
    get_paginated_response,
    get_paginated_response_context,
)
from .permissions import IsOwnerOrReadOnly
from .serializers import CategorySerializer, PostSerializer

User = get_user_model()


class PostViewSet(ViewSet):
    # queryset = get_posts()
    serializer_class = PostSerializer
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    class FilterSerializer(serializers.Serializer):
        """
        These fields are used in the filters.py
        """

        title = serializers.CharField(required=False, max_length=100)
        search = serializers.CharField(required=False, max_length=100)
        author__in = serializers.CharField(required=False, max_length=100)
        category__name = serializers.CharField(required=False, max_length=100)
        created_at__range = serializers.CharField(required=False, max_length=100)

    def list(self, request):
        request = self.request
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        try:
            queryset = get_posts(filters=filter_serializer.validated_data)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return get_paginated_response_context(
            pagination_class=PageNumberPagination,
            serializer_class=PostSerializer,
            queryset=queryset,
            request=request,
            view=self,
        )
        # return Response(serializer.data, status=status.HTTP_200_OK)

    # @swagger_auto_schema(request_body=PostSerializer, response=PostSerializer)
    def partial_update(self, request, slug):
        post = Post.objects.get(slug=slug)
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
                {"detail": "Post does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        # serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, slug):

        try:
            post = get_post(slug)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug):
        try:
            delete_post(slug)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

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
