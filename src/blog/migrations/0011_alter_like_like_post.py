# Generated by Django 4.1.5 on 2023-03-12 06:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0010_alter_like_like_post"),
    ]

    operations = [
        migrations.AlterField(
            model_name="like",
            name="like_post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="like",
                to="blog.post",
            ),
        ),
    ]
