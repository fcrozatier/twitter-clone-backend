from random import randint

import factory
from faker import Faker

from accounts.models import User
from api.models import TweetNode

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = fake.first_name()
    email = fake.email()
    password = fake.password(length=10)
