import factory

# from django.contrib.auth import get_user_model
from faker import Faker

from accounts.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = fake.first_name()
    email = fake.email()
    password = fake.password(length=10)
