from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

from blog.models import Post, Comment

User = get_user_model()


@transaction.atomic
def create_post(user, category, title, content, image, status, published_at):
    return Post.objects.create(
        author=user,
        category=category,
        title=title,
        slug=slugify(title),
        content=content,
        image=image,
        status=status,
        published_at=published_at,
    )


def delete_post(slug):
    return Post.objects.get(slug=slug).delete()


# post.category = validated_data["category"]
# post.title = validated_data["title"]
# post.slug = slugify(post.title)
# post.content = validated_data["content"]
# post.image = validated_data["image"]
# post.status = validated_data["status"]


# Post.objects.filter(slug=slug).update(**validated_data)
@transaction.atomic
def update_post(validated_data, author, slug):
    post = Post.objects.get(slug=slug)
    post.author = author

    if "category" in validated_data:
        post.category = validated_data["category"]
    if "title" in validated_data:
        post.title = validated_data["title"]

    if "slug" in validated_data:
        post.slug = validated_data["slug"]
    if "content" in validated_data:
        post.content = validated_data["content"]
    if "image" in validated_data:
        post.image = validated_data["image"]
    if "status" in validated_data:
        post.status = validated_data["status"]
    if "published_at" in validated_data:
        post.published_at = validated_data["published_at"]

    post.full_clean()
    post.save()
    return post


def create_comment(user, post, comment):
    return Comment.objects.create(comment_user=user, comment_post=post, comment=comment)


def update_comment(comment, pk):
    get_comment = Comment.objects.get(pk=pk)
    get_comment.comment = comment

    get_comment.full_clean()
    get_comment.save()
    return get_comment


def delete_comment(pk):
    return Comment.objects.get(pk=pk).delete()
