from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from django.db.models import QuerySet
from django_filters.rest_framework import filters, FilterSet
from django_filters.rest_framework import DjangoFilterBackend

from blog.models import Post
from blog.api.v1.filters import PostFilter

User = get_user_model()


def get_author(request):
    return User.objects.get(id=request.user.id)


def get_slug():
    queryset = Post.objects.select_related("author", "category").all()
    for post in queryset:
        return post.slug


def get_posts(filters=None):
    queryset = Post.objects.select_related("author", "category").filter(status=True)
    filters = filters or {}

    return PostFilter(filters, queryset).qs


def get_post(slug):
    return (
        Post.objects.select_related("author", "category")
        .filter(status=True)
        .get(slug=slug)
    )
