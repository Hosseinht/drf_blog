from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(email, first_name, last_name, password):
    return User.objects.create_user(
        email=email, first_name=first_name, last_name=last_name, password=password
    )


def update_profile(instance, user, bio, image, birth_date):
    profile = instance

    profile.user.first_name = user["first_name"]
    profile.user.last_name = user["last_name"]
    profile.user.full_clean()
    profile.user.save()

    profile.bio = bio
    profile.image = image
    profile.birth_date = birth_date

    profile.full_clean()
    profile.save()

    return profile
