import pytest
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


@pytest.mark.parametrize("user__username", ["John"])
def test_user_str(db, user):
    assert user.__str__() == "John"


@pytest.mark.django_db
class TestAccounts:
    def test_create_user(self, valid_user_payload):
        response = graphql_query(mutation_create_user, variables=valid_user_payload()).json()
        print(response)
        response = graphql_query(mutation_create_user, variables=valid_user_payload()).json()
        print(response)
        response = graphql_query(mutation_create_user, variables=valid_user_payload()).json()
        print(response)
        response = graphql_query(mutation_create_user, variables=valid_user_payload()).json()
        print(response)
        assert response["data"]["register"]["success"] is True
        assert response["data"]["register"]["errors"] == None

    def test_list_users(self, create_user, client):
        response = graphql_query(query_list_users, client=client).json()
        print(response)
        assert len(response["data"]["users"]["edges"]) == 1

    def test_user_creation_replicates_in_neodb(db, create_user):
        user = create_user
        response = graphql_query(query_list_users).json()
        print(user.uid)
        print(response)
        assert response["data"]["users"]["edges"][0]["node"]["uid"] == str(user.uid)
