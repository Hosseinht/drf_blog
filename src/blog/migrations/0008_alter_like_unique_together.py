# Generated by Django 4.1.5 on 2023-03-09 07:36

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("blog", "0007_like"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="like",
            unique_together={("like_user", "like_post")},
        ),
    ]
