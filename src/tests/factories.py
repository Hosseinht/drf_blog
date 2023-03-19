import factory
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from accounts.models import User
from blog.models import Category, Comment, Like, Post

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    # username = factory.Sequence(lambda n: "john%s" % n)
    email = factory.Sequence(lambda n: "%s@example.org" % n)
    first_name = fake.first_name()
    last_name = fake.last_name()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.LazyAttribute(lambda _: f"{fake.text(max_nb_chars=5)}")


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    title = factory.Sequence(lambda n: "test_name_%d" % n)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))
    content = factory.Sequence(lambda n: "test_content_%d" % n)
    image = factory.django.ImageField(
        filename="test_image.jpg",
        width=800,
        height=800,
        color="green",
        format="JPEG",
    )
    status = True
    published_at = timezone.now()


class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Like

    like_user = factory.SubFactory(UserFactory)
    like_post = factory.SubFactory(PostFactory)


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    comment_user = factory.SubFactory(UserFactory)
    comment_post = factory.SubFactory(PostFactory)
    comment = factory.lazy_attribute(lambda _: f"{fake.text(max_nb_chars=5)}")
