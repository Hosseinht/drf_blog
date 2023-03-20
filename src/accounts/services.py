from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(email, first_name, last_name, password):
    return User.objects.create_user(
        email=email, first_name=first_name, last_name=last_name, password=password
    )
