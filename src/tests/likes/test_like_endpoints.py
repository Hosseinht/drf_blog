import pytest
from django.urls import reverse
from rest_framework import status

from blog.models import Like

pytestmark = pytest.mark.django_db


post_url = reverse("blog:api-v1:posts-list")


class TestLikes:
    def test_anonymous_user_can_not_like_a_post_return_401(
        self, api_client, media_root, create_post
    ):

        response = api_client.post(f"{post_url}{create_post.slug}/likes/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_like(self, api_client, user_factory, post_factory, media_root):
        user = user_factory.create()
        post = post_factory.create()

        api_client.force_authenticate(user=user)

        response = api_client.post(f"{post_url}{post.slug}/likes/")

        assert response.status_code == status.HTTP_200_OK
        assert Like.objects.filter(like_user=user, like_post=post).exists()

    def test_delete_like(
        self, api_client, user_factory, post_factory, like_factory, media_root
    ):
        user = user_factory.create()
        post = post_factory.create()

        like_factory.create(like_user=user, like_post=post)

        api_client.force_authenticate(user=user)

        response = api_client.post(f"{post_url}{post.slug}/likes/")

        assert response.status_code == status.HTTP_200_OK
        assert not Like.objects.filter(like_user=user, like_post=post).exists()

    def test_like_count(self, user_factory, post_factory, like_factory, media_root):
        user = user_factory.create_batch(size=2)
        post = post_factory.create_batch(size=2)

        like_factory.create(like_user=user[0], like_post=post[0])
        like_factory.create(like_user=user[1], like_post=post[1])

        assert Like.objects.count() == 2
