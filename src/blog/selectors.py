from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework.exceptions import NotFound

from blog.api.v1.filters import PostFilter
from blog.models import Comment, Post

User = get_user_model()


def get_posts(filters=None):
    queryset = (
        Post.objects.select_related("author", "category")
        .prefetch_related("comments__comment_user")
        .annotate(likes=Count("like__id"))
        .filter(status=True)
    )
    filters = filters or {}

    return PostFilter(filters, queryset).qs


def get_post(slug):
    return (
        Post.objects.select_related("author", "category")
        .prefetch_related("comments__comment_user")
        .annotate(likes=Count("like__id"))
        .filter(status=True)
        .get(slug=slug)
    )


def get_comments(post_slug):
    if not Post.objects.filter(slug=post_slug).exists():
        raise NotFound({"detail": "Post not found."})

    return Comment.objects.select_related(
        "comment_user",
        "comment_post",
    ).filter(comment_post__slug=post_slug)


def get_comment(pk):
    return Comment.objects.get(pk=pk)
