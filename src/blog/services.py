from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

from blog.models import Post

User = get_user_model()


@transaction.atomic
def create_post(validated_data, user):
    # author = User.objects.get(id=user.id)
    return Post.objects.create(
        author=user,
        **validated_data,
    )


def delete_post(slug):
    # author = User.objects.get(id=user.id)
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
        post.slug = slugify(post.title)
    if "content" in validated_data:
        post.content = validated_data["content"]
    if "image" in validated_data:
        post.image = validated_data["image"]
    if "status" in validated_data:
        post.status = validated_data["status"]

    post.full_clean()
    post.save()
    return post
