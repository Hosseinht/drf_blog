from django.contrib.auth import get_user_model

from blog.models import Post

User = get_user_model()


def create_post(validated_data, user):
    # author = User.objects.get(id=user.id)
    return Post.objects.create(
        author=user,
        **validated_data,
    )
