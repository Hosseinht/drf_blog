import json

import pytest
from django.forms import model_to_dict
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


post_url = reverse("blog:api-v1:posts-list")


class TestCreatePost:
    def test_anonymous_user_can_not_create_book_return_401(
        self, api_client, media_root
    ):
        response = api_client.post(post_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_create_post_return_201(
        self, api_client, post_factory, user_factory, media_root
    ):
        author = user_factory.create()
        post1 = post_factory.create(author=author)
        print(author)
        print(post1)
        api_client.force_authenticate(author)

        post_data = {
            "category": post1.category.id,
            "title": "title",
            "content": "content",
            "image": post1.image,
            "status": True,
            "published_at": post1.published_at,
        }

        response = api_client.post(post_url, post_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0

    def test_data_is_invalid_return_400(
        self, api_client, post_factory, user_factory, media_root
    ):
        author = user_factory.create()
        post1 = post_factory.create(author=author)

        api_client.force_authenticate(author)

        post_data = {
            "category": post1.category.id,
            "title": "",
            "content": "content",
            "image": post1.image,
            "status": True,
            "published_at": post1.published_at,
        }

        response = api_client.post(post_url, post_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None


class TestGetPost:
    def test_get_list_of_posts_return_200(self, api_client, post_factory, media_root):

        post_factory.create_batch(4)

        response = api_client.get(post_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(json.loads(response.content)) == 4

    def test_get_a_single_post_return_200(self, api_client, create_post, media_root):
        response = api_client.get(f"{post_url}{create_post.slug}/")

        assert response.status_code == status.HTTP_200_OK

    def test_if_post_exist_return_200(self, api_client, create_post, media_root):
        response = api_client.get(f"{post_url}{create_post.slug}/")
        response_data = response.data["results"]

        assert response.status_code == status.HTTP_200_OK
        assert response_data["id"] == create_post.id
        assert response_data["category"] == create_post.category.name
        assert response_data["content"] == create_post.content
        assert response_data["image"] == f"http://testserver/media/{create_post.image}"
        assert response_data["status"] == create_post.status
        assert response_data["published_at"] == create_post.published_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        # assert create_post.image.url in response.data["image"]

    def test_if_post_doesnt_exist_return_404(self, api_client):
        response = api_client.get(f"{post_url}test_slug/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filter_posts_return_200(
        self, api_client, post_factory, category_factory, media_root
    ):
        category1 = category_factory.create(name="sport")
        category2 = category_factory.create(name="technology")
        post1 = post_factory.create(category=category1)
        post2 = post_factory.create(category=category1)
        post3 = post_factory.create(category=category2)

        response = api_client.get(f"{post_url}?category__name=sport")

        assert len(response.data["results"]) == 2

    def test_search_posts_return_200(self, api_client, post_factory, media_root):

        post1 = post_factory.create(title="title")
        post2 = post_factory.create(title="post")

        response = api_client.get(f"{post_url}?search=title")

        assert len(response.data["results"]) == 1


class TestUpdatePost:
    def test_anonymous_user_can_not_update_post_return_401(
        self, api_client, create_post, media_root
    ):

        response = api_client.put(f"{post_url}{create_post.slug}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_not_update_others_posts_return_403(
        self, api_client, user_factory, post_factory, media_root
    ):

        user1 = user_factory.create()
        user2 = user_factory.create()

        post = post_factory.create(author=user1)

        api_client.force_authenticate(user2)

        response = api_client.patch(f"{post_url}{post.slug}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_posts_return_200(
        self,
        api_client,
        user_factory,
        post_factory,
        media_root,
    ):

        user = user_factory.create()

        post = post_factory.create(author=user)
        updated_post = post_factory.create(author=user)
        updated_post.slug = "new_slug"
        # to ensure that the updated_post has a different slug than the one generated by the post_factory so
        # the test is not going to violate the unique constraint on the slug field

        api_client.force_authenticate(user)

        response = api_client.patch(
            f"{post_url}{post.slug}/", model_to_dict(updated_post)
        )

        post.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert post.title == updated_post.title
        assert post.slug == updated_post.slug
        assert post.content == updated_post.content
        assert post.status == updated_post.status


class TestDeletePost:
    def test_anonymous_user_can_not_delete_post_return_401(
        self, api_client, create_post, media_root
    ):
        response = api_client.delete(f"{post_url}{create_post.slug}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_not_delete_others_posts_return_403(
        self, api_client, user_factory, post_factory, media_root
    ):
        user1 = user_factory.create()
        user2 = user_factory.create()

        post = post_factory.create(author=user1)

        api_client.force_authenticate(user2)

        response = api_client.delete(f"{post_url}{post.slug}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_post_return_204(
        self, api_client, user_factory, post_factory, media_root
    ):
        user = user_factory.create()

        post = post_factory.create(author=user)

        api_client.force_authenticate(user)

        response = api_client.delete(f"{post_url}{post.slug}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
