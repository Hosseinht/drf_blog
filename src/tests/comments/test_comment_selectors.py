import pytest

from blog.selectors import get_comment, get_comments

pytestmark = pytest.mark.django_db


def test_get_comments_list(media_root, create_user, create_post, comment_factory):
    comments = comment_factory.create_batch(
        size=2, comment_user=create_user, comment_post=create_post
    )

    comment_list = get_comments(create_post.slug)

    assert comment_list.first() == comments[0]
    assert comment_list.count() == 2


def test_get_single_post(media_root, create_user, create_post, comment_factory):
    comments = comment_factory.create_batch(
        size=2, comment_user=create_user, comment_post=create_post
    )

    comment = get_comment(comments[0].id)

    assert comment.id == comments[0].id
    assert comment.comment == comments[0].comment
