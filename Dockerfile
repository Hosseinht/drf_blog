# base image
FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install libpq-dev gcc

WORKDIR /app

COPY ./requirements /app/requirements

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements/production.txt

COPY ./src /app

