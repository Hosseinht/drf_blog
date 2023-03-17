from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from blog.models import Category, Like, Post, Comment
from blog.selectors import get_post, get_posts, get_comments, get_comment
from blog.services import (
    create_post,
    delete_post,
    update_post,
    create_comment,
    update_comment,
    delete_comment,
)

from .paginations import (
    PostPagination,
    get_paginated_response,
    get_paginated_response_context,
)
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrReadOnly
from .serializers import (
    CategorySerializer,
    FilterSerializer,
    PostSerializer,
    CommentSerializer,
)

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


class CommentViewSet(ViewSet):
    serializer = CommentSerializer

    def list(self, request, post_slug):
        queryset = get_comments(post_slug=post_slug)

        return get_paginated_response_context(
            pagination_class=PostPagination,
            serializer_class=CommentSerializer,
            queryset=queryset,
            request=request,
            view=self,
        )

    def create(self, request, post_slug):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = request.user

        try:
            post = get_post(slug=post_slug)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

        create_comment(
            user=user,
            post=post,
            comment=validated_data.get("comment"),
        )

        # serializer = self.serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        try:
            comment = get_comment(pk=self.kwargs["pk"])
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        comment = get_comment(pk=self.kwargs["pk"])
        serializer = self.serializer(data=request.data, instance=comment)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        update_comment(comment=validated_data.get("comment"), pk=self.kwargs["pk"])

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            delete_comment(pk=self.kwargs["pk"])
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
