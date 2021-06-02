import pytest
from django.contrib.auth import get_user_model
from faker import Faker
from graphene_django.utils.testing import graphql_query

mutation_create_user = """
mutation createUser(
    $email: String!,
    $username: String!,
    $password1: String!,
    $password2: String!
    ) {
  register(
    email:$email,
    username: $username,
    password1: $password1,
    password2: $password2) {
      success
      errors
  }
}
"""

query_list_users = """
query {
  users(isActive: true){
    edges {
      node {
        id
        username
        email
        isActive
        verified
      }
    }
  }
}
"""


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


@pytest.mark.django_db
class TestAccounts:
    def test_create_user(self, fake):
        password = fake.password(length=10)
        payload = {
            "email": fake.email(),
            "username": fake.first_name(),
            "password1": password,
            "password2": password,
        }
        response = graphql_query(mutation_create_user, variables=payload).json()
        assert response["data"]["register"]["success"] is True
        assert response["data"]["register"]["errors"] == None

    def test_list_users(self, create_user):
        response = graphql_query(query_list_users).json()
        assert len(response["data"]["users"]["edges"]) == 1
