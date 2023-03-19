import os
import shutil

import pytest
from django.conf import settings
from pytest_factoryboy import register
from rest_framework.test import APIClient

from tests.factories import (
    CategoryFactory,
    LikeFactory,
    PostFactory,
    UserFactory,
    CommentFactory,
)

register(UserFactory)
register(CategoryFactory)
register(PostFactory)
register(LikeFactory)
register(CommentFactory)


@pytest.fixture
def media_root():
    """
    This function change the media root to tests/test_data/media/posts
    and after the test is finished it will delete the photo
    """
    path = os.path.join(settings.BASE_DIR, "tests/test_data/media/posts")
    os.makedirs(path, exist_ok=True)
    settings.MEDIA_ROOT = path
    yield
    shutil.rmtree(path)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture()
def create_user(db, user_factory):
    return user_factory.create()


@pytest.fixture()
def create_post(db, post_factory):
    return post_factory.create()


@pytest.fixture()
def create_category(db, category_factory):
    return category_factory.create()


@pytest.fixture()
def create_author(db, user_factory):
    return user_factory.create()


@pytest.fixture()
def create_comment(db, comment_factory, create_post, create_user):
    return comment_factory.create(comment_user=create_user, comment_post=create_post)


@pytest.fixture()
def book_payload(db, create_post, create_author):
    author = create_author
    post = create_post(
        author=author,
        category=create_post.category.id,
        title="Title 1",
        slug="title_1",
        content="This is content",
        image=create_post.image,
        status=True,
        created_at=create_post.created_at,
        updated_at=create_post.updated_at,
        published_at=create_post.published_at,
    )
