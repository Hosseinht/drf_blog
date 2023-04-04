from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


def create_user(email, first_name, last_name, password):
    return User.objects.create_user(
        email=email, first_name=first_name, last_name=last_name, password=password
    )


@transaction.atomic
def update_profile(instance, validated_data):

    user_data = validated_data.pop("user", {})
    user = instance.user
    for key, value in user_data.items():
        setattr(user, key, value)
        user.save()

    for key, value in validated_data.items():
        setattr(instance, key, value)
        instance.save()

    return instance
