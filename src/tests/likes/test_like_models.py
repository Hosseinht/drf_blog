import pytest

from django.db import IntegrityError


pytestmark = pytest.mark.django_db


def test_unique_together_constraint(user_factory, post_factory, like_factory):
    user = user_factory.create()
    post = post_factory.create()

    like_factory.create(like_user=user, like_post=post)

    with pytest.raises(IntegrityError):
        like_factory.create(like_user=user, like_post=post)
