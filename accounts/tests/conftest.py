import pytest
from django.contrib.auth import get_user_model
from faker import Faker
from neomodel import db


@pytest.fixture(autouse=True, scope="session")
def setup_neo_test_db():
    print("Initializing test session fixture !")
    db.begin()
    yield
    print("Tear down session !")
    db.rollback()


@pytest.fixture(scope="module")
def fake():
    return Faker()


@pytest.fixture()
def create_user(db, fake):
    password = fake.password(length=10)
    payload = {
        "email": fake.email(),
        "username": fake.first_name(),
        "password": password,
    }
    user = get_user_model().objects.create(**payload)
    return user
