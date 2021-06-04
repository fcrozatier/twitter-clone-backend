import pytest
from graphene_django.utils.testing import graphql_query

from .conftest import fake

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
        uid
        username
        email
        isActive
        verified
      }
    }
  }
}
"""


def valid_user_payload(fake):
    password = fake.password(length=10)
    payload = {
        "email": fake.email(),
        "username": fake.first_name(),
        "password1": password,
        "password2": password,
    }

    return payload


@pytest.mark.django_db
class TestAccounts:
    def test_create_user(self, fake):
        response = graphql_query(mutation_create_user, variables=valid_user_payload(fake)).json()
        print(response)
        response = graphql_query(mutation_create_user, variables=valid_user_payload(fake)).json()
        print(response)
        response = graphql_query(mutation_create_user, variables=valid_user_payload(fake)).json()
        print(response)
        response = graphql_query(mutation_create_user, variables=valid_user_payload(fake)).json()
        print(response)
        assert response["data"]["register"]["success"] is True
        assert response["data"]["register"]["errors"] == None

    def test_list_users(self, create_user):
        response = graphql_query(query_list_users).json()
        print(response)
        assert len(response["data"]["users"]["edges"]) == 1
