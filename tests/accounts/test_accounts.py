import pytest
import tests.queries as queries
from api.models import UserNode
from graphene_django.utils.testing import graphql_query


@pytest.mark.parametrize("user__username", ["John"])
def test_user_str(db, user):
    assert user.__str__() == "John"


@pytest.mark.django_db
class TestAccounts:
    def test_create_user(self, valid_user_payload):
        response = graphql_query(queries.create_user, variables=valid_user_payload()).json()
        print(response)
        assert response["data"]["register"]["success"] is True
        assert response["data"]["register"]["errors"] == None

    def test_list_users(self, create_user, client):
        response = graphql_query(queries.list_users, client=client).json()
        print(response)
        assert len(response["data"]["users"]["edges"]) == 1

    def test_user_creation_replicates_in_neodb(db, valid_user_payload):
        payload = valid_user_payload()
        email = payload["email"]
        # create a user in the db via graphql to trigger the replication signal
        graphql_query(queries.create_user, variables=payload)

        # get the user from postgres to check its uid
        response = graphql_query(queries.list_users_by_email, variables={"email": email}).json()
        uid = response["data"]["users"]["edges"][0]["node"]["uid"]
        print(uid)

        # query neodb to verify the UserNode with this id exists
        user = UserNode.nodes.get_or_none(uid=uid)
        print(user)
        assert user is not None
