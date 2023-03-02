from django.contrib.auth import get_user_model
from django.db.models import Value

from blog.models import Post

User = get_user_model()


def get_author(request):
    return User.objects.get(id=request.user.id)


def get_slug():
    queryset = Post.objects.select_related("author", "category").all()
    for post in queryset:
        return post.slug


def get_posts():
    return Post.objects.select_related("author", "category").all()


def get_post(slug):
    return Post.objects.select_related("author", "category").filter(slug=slug)

# def get_absolute_url(self, obj):
#     request = self.context.get("request")
#     return request.build_absolute_uri(obj.slug)
