import pytest

from blog.models import Comment
from blog.services import create_comment, delete_comment, update_comment

pytestmark = pytest.mark.django_db


class TestCommentServices:
    def test_create_comment(self, media_root, create_post, create_user):
        comment = create_comment(
            user=create_user, post=create_post, comment="Test comment"
        )

        assert comment.comment_user == create_user
        assert comment.comment_post == create_post
        assert comment.comment == "Test comment"

    def test_update_comment(
        self, media_root, create_post, create_user, comment_factory
    ):
        comment = comment_factory.create(
            comment_user=create_user, comment_post=create_post
        )

        update_comment(comment="updated comment", pk=comment.pk)

        comment.refresh_from_db()

        assert comment.comment == "updated comment"

    def test_delete_comment(
        self, media_root, create_post, create_user, comment_factory
    ):

        comment = comment_factory.create(
            comment_user=create_user, comment_post=create_post
        )

        delete_comment(comment.pk)

        with pytest.raises(Comment.DoesNotExist):
            Comment.objects.get(pk=comment.pk)
