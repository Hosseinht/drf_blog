from rest_framework.test import APIClient
from django.urls import reverse
import pytest
from datetime import datetime
from accounts.models import User

from blog.models import Category


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def common_user():
    user = User.objects.create_user(
        email="admin@admin.com", first_name="Gholi", last_name="Moli", password="a/@1234567", is_verified=True
    )
    return user


@pytest.fixture
def category():
    category = Category.objects.create(name='sport')
    return category


@pytest.mark.django_db
class TestPostApi:
    def test_get_post_response_200_status(self, api_client):
        url = reverse("blog:api-v1:posts-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_create_post_response_401_status(self, api_client):
        url = reverse("blog:api-v1:posts-list")
        data = {
            "title": "test",
            "content": "description",
            "status": True,
            "published_date": datetime.now(),
        }
        response = api_client.post(url, data)

        assert response.status_code == 401

    def test_create_post_response_201_status(self, api_client, category, common_user):
        url = reverse("blog:api-v1:posts-list")
        data = {
            "category": category.pk,
            "title": "test",
            "content": "description",
            "status": True,
            "published_date": datetime.now(),
        }
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data)
        print(response.data)
        assert response.status_code == 201

    def test_create_post_invalid_data_response_400_status(
            self, api_client, common_user
    ):
        url = reverse("blog:api-v1:posts-list")
        data = {"title": "test", "content": "description"}
        user = common_user

        api_client.force_authenticate(user=user)
        response = api_client.post(url, data)
        assert response.status_code == 400
