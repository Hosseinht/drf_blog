import pytest

from blog.selectors import get_post, get_posts

pytestmark = pytest.mark.django_db


def test_get_posts_list(media_root, user_factory, post_factory):
    author = user_factory.create()
    posts = post_factory.create_batch(size=2, author=author)

    post_list = get_posts()

    assert post_list.first() == posts[0]
    assert post_list.count() == 2


def test_get_single_post(media_root, user_factory, post_factory):
    author = user_factory.create()
    post1 = post_factory.create(author=author)
    post2 = post_factory.create(author=author)

    post = get_post(slug=post1.slug)

    assert post.slug == post1.slug
    assert post.author == post1.author
