import random
from datetime import datetime

from django.core.management.base import BaseCommand
from accounts.models import User, Profile
from blog.models import Post, Category
from faker import Faker

category_list = [
    'Sport',
    'Technology',
    'Food',
    'Space',
    'Crypto'
]


class Command(BaseCommand):
    help = 'Inserting dummy data'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):
        user = User.objects.create_user(email=self.fake.email(), first_name=self.fake.first_name(),
                                        last_name=self.fake.last_name(), password='p@ssword', )
        profile = Profile.objects.get(user=user)
        profile.bio = self.fake.paragraph(nb_sentences=5)
        profile.birth_date = self.fake.date()
        profile.save()

        for category in category_list:
            Category.objects.get_or_create(name=category)

        for _ in range(10):
            Post.objects.create(
                author=user,
                title=self.fake.paragraph(nb_sentences=1),
                content=self.fake.paragraph(nb_sentences=10),
                status=random.choice([True, False]),
                category=Category.objects.get(name=random.choice(category_list)),
                published_at=datetime.now(),
            )