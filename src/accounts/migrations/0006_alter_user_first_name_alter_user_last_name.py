# Generated by Django 4.1.5 on 2023-01-05 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "accounts",
            "0005_remove_profile_first_name_remove_profile_last_name_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(max_length=250),
        ),
    ]
