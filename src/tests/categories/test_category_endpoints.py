import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()

pytestmark = pytest.mark.django_db

category_url = reverse("blog:api-v1:categories-list")


class TestCreateCategory:
    def test_anonymous_user_can_not_create_category_return_401(
        self,
        api_client,
    ):
        response = api_client.post(category_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_common_user_can_not_create_category_return_403(
        self, api_client, user_factory
    ):
        user = user_factory.create()

        api_client.force_authenticate(user=user)

        response = api_client.post(category_url, data={"name": "test category"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_create_category_return_201(self, api_client):
        api_client.force_authenticate(user=User(is_staff=True))

        response = api_client.post(category_url, data={"name": "test category"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0

    def test_data_is_invalid_return_400(self, api_client):
        api_client.force_authenticate(user=User(is_staff=True))

        response = api_client.post(category_url, data={"name": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetCategory:
    def test_get_list_of_categories_return_200(self, api_client, category_factory):
        category_factory.create_batch(size=4)

        response = api_client.get(category_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(json.loads(response.content)) == 4

    def test_get_a_single_category_return_200(self, api_client, create_category):
        response = api_client.get(f"{category_url}{create_category.id}/")

        assert response.status_code == status.HTTP_200_OK

    def test_if_category_exist_return_200(self, api_client, create_category):
        response = api_client.get(f"{category_url}{create_category.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == create_category.id
        assert response.data["name"] == create_category.name

    def test_if_category_doesnt_exist_return_400(self, api_client, create_category):
        response = api_client.get(f"{category_url}1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateCategory:
    def test_anonymous_user_can_not_update_category_return_401(
        self,
        api_client,
    ):
        response = api_client.put(category_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_common_user_can_not_update_category_return_403(
        self, api_client, user_factory, create_category
    ):
        user = user_factory.create()

        api_client.force_authenticate(user=user)

        response = api_client.put(
            f"{category_url}{create_category.id}/", data={"name": "update category"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_update_category_return_201(self, api_client, category_factory):
        category = category_factory.create()
        api_client.force_authenticate(user=User(is_staff=True))

        response = api_client.put(
            f"{category_url}{category.id}/", data={"name": "update category"}
        )

        category.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert category.name == "update category"


class TestDeleteCategory:
    def test_anonymous_user_can_not_delete_category_return_401(
        self,
        api_client,
    ):
        response = api_client.delete(category_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_common_user_can_not_delete_category_return_403(
        self, api_client, user_factory, create_category
    ):
        user = user_factory.create()

        api_client.force_authenticate(user=user)

        response = api_client.delete(f"{category_url}{create_category.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_user_delete_category_return_201(self, api_client, create_category):

        api_client.force_authenticate(user=User(is_staff=True))

        response = api_client.delete(f"{category_url}{create_category.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None
