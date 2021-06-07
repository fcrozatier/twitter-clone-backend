import pytest
from faker import Faker
from neomodel import db
from pytest_factoryboy import register

from .factories import UserFactory


@pytest.fixture(autouse=True, scope="session")
def setup_neo_test_db():
    print("Initializing test session fixture !")
    db.begin()
    yield
    print("Tear down session !")
    db.rollback()


register(UserFactory)


@pytest.fixture
def create_user(db, user_factory):
    user = user_factory.create()
    return user


@pytest.fixture
def valid_user_payload(faker):
    def make_valid_user_payload():
        password = faker.password(length=10)
        payload = {
            "email": faker.email(),
            "username": faker.first_name(),
            "password1": password,
            "password2": password,
        }

        return payload

    return make_valid_user_payload
