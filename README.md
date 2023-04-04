# DRF Blog API
Blog with Django REST framework

## Features

- JWT Authentication
- Full text search
- Write comments for a post
- Add posts to favorite list
- Filtering and Pagination
- Like a blog post
- Delete unverified users after a week

## Stack

- [Python](https://www.python.org/) 
- [Django](https://docs.djangoproject.com/en/3.2/releases/3.2/) 
- [Django Rest Framework ](https://www.django-rest-framework.org/) 
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
- [PostgreSQL](https://www.postgresql.org/)
- [Pytest](https://docs.pytest.org/en/7.2.x/)
- [Celery](https://docs.celeryq.dev/en/stable/)
- [Docker](https://www.docker.com/)
- [Redis](https://redis.io/)

## Installation

Clone the project

```bash
  git clone https://github.com/Hosseinht/drf_blog && cd drf_blog
```

**Create .env file. Provide needed information(check .env.example)**

Install Docker
- [install Docker in Linux](https://docs.docker.com/engine/install/)
- [install Docker in Windows](https://docs.docker.com/desktop/windows/install/)
- [install Docker in Mac](https://docs.docker.com/desktop/mac/install/)

**docker-compose**
- [install docker-compose](https://docs.docker.com/compose/install/)

**Build and run the app**
```shell
docker-compose build
```
```shell
docker-compose up
```

## Endpoints

To see the endpoints go to http://127.0.0.1:8000/swagger/