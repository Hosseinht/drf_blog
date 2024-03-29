# Generated by Django 4.1.5 on 2023-03-12 06:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0008_alter_like_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="like",
            name="like_post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="likes",
                to="blog.post",
            ),
        ),
    ]
