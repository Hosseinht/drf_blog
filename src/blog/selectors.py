from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.postgres.search import SearchVector
from django_filters.rest_framework import filters

from blog.models import Post

User = get_user_model()


def get_author(request):
    return User.objects.get(id=request.user.id)


def get_slug():
    queryset = Post.objects.select_related("author", "category").all()
    for post in queryset:
        return post.slug


def filter_queryset(queryset):
    for backend in list(filters.DjangoFilterBackend):
        queryset = backend().filter_queryset(queryset)
    return queryset


def get_posts(request):
    queryset = Post.objects.select_related("author", "category").filter(status=True)
    search_query = request.query_params.get("search", None)

    filter_qs = filter_queryset(queryset)

    if search_query:
        posts = Post.objects.annotate(search=SearchVector("title", "content")).filter(
            search=search_query
        )
        return posts
    else:
        return queryset


def get_post(slug):
    return (
        Post.objects.select_related("author", "category")
        .filter(status=True)
        .get(slug=slug)
    )


# def get_absolute_url(self, obj):
#     request = self.context.get("request")
#     return request.build_absolute_uri(obj.slug)
