import json

import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


post_url = reverse("blog:api-v1:posts-list")


class TestCreateComment:
    def test_anonymous_user_can_not_write_comment_return_401(self, api_client):

        response = api_client.post(f"{post_url}comments/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_write_comment_return_201(
        self, api_client, user_factory, post_factory, media_root
    ):
        user = user_factory.create()
        post = post_factory.create()

        api_client.force_authenticate(user=user)

        response = api_client.post(
            path=f"{post_url}{post.slug}/comments/",
            data={
                "comment": "Test comment",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0

    def test_data_is_invalid_return_400(
        self, api_client, user_factory, post_factory, media_root
    ):
        user = user_factory.create()
        post = post_factory.create()

        api_client.force_authenticate(user=user)

        response = api_client.post(
            path=f"{post_url}{post.slug}/comments/",
            data={
                "comment": "",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetComment:
    def test_get_list_of_comments_return_200(
        self, api_client, post_factory, user_factory, comment_factory, media_root
    ):
        user = user_factory.create()
        post = post_factory.create()
        comment_factory.create_batch(size=2, comment_user=user, comment_post=post)

        response = api_client.get(f"{post_url}{post.slug}/comments/")
        json_response = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert len(json_response["results"]) == 2

    def test_get_a_single_comment_return_200(
        self, api_client, create_comment, create_post, media_root
    ):

        response = api_client.get(
            f"{post_url}{create_post.slug}/comments/{create_comment.id}/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] > 0

    def test_if_comment_exist_return_200(
        self, api_client, create_comment, create_post, media_root
    ):
        response = api_client.get(
            f"{post_url}{create_post.slug}/comments/{create_comment.id}/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == create_comment.id
        assert response.data["comment_user"] == create_comment.comment_user.email
        assert response.data["comment_post"] == create_comment.comment_post.title
        assert response.data["comment"] == create_comment.comment
        assert response.data["created_at"] == create_comment.created_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def test_comment_does_not_exist_return_404(
        self, api_client, create_comment, create_post, media_root
    ):

        response = api_client.get(f"{post_url}{create_post.slug}/comments/3/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateComment:
    def test_anonymous_user_can_not_update_comment_return_401(
        self, media_root, api_client, create_comment, create_post
    ):

        response = api_client.put(
            f"{post_url}{create_post.slug}/comments/{create_comment.id}/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_comment_return_200(
        self, api_client, comment_factory, user_factory, create_post, media_root
    ):
        user = user_factory.create()
        post = create_post
        comment = comment_factory.create(comment_user=user, comment_post=post)

        api_client.force_authenticate(user)

        response = api_client.put(
            f"{post_url}{create_post.slug}/comments/{comment.id}/",
            data={"comment": "New comment"},
        )

        comment.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert comment.comment == "New comment"

    def test_authenticated_user_can_not_update_others_comments_return_403(
        self, api_client, create_post, user_factory, comment_factory, media_root
    ):
        user1 = user_factory.create()
        user2 = user_factory.create()

        comment = comment_factory.create(comment_user=user1, comment_post=create_post)

        api_client.force_authenticate(user2)

        response = api_client.put(
            f"{post_url}{create_post.slug}/comments/{comment.id}/",
            data={"comment": "New comment"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteComment:
    def test_anonymous_user_can_not_delete_comment_return_401(
        self, api_client, media_root, create_comment, create_post
    ):

        response = api_client.delete(
            f"{post_url}{create_post.slug}/comments/{create_comment.id}/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_comment_return_204(
        self, api_client, media_root, create_user, create_post, comment_factory
    ):
        comment = comment_factory.create(
            comment_user=create_user, comment_post=create_post
        )

        api_client.force_authenticate(user=create_user)

        response = api_client.delete(
            f"{post_url}{create_post.slug}/comments/{comment.id}/"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None

    def test_authenticated_user_can_not_delete_others_comments_return_403(
        self, api_client, media_root, user_factory, create_post, comment_factory
    ):
        user1 = user_factory.create()
        user2 = user_factory.create()

        comment = comment_factory.create(comment_user=user1, comment_post=create_post)

        api_client.force_authenticate(user2)

        response = api_client.delete(
            f"{post_url}{create_post.slug}/comments/{comment.id}/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
