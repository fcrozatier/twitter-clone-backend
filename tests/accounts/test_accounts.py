import pytest
import tests.queries as queries
from api.errors import USER_ALREADY_FOLLOWED_ERROR, USER_NOT_FOUND_ERROR
from api.models import UserNode
from graphene_django.utils.testing import graphql_query


@pytest.mark.parametrize("user__username", ["John"])
def test_user_str(db, user):
    assert user.__str__() == "John"


@pytest.mark.django_db
class TestAccounts:
    def test_create_user(self, create_user_node):
        response = create_user_node(response=True)
        print(response)
        assert "errors" not in response

    def test_last_user(self, create_user_node):
        create_user_node()
        response = graphql_query(queries.last_user).json()
        print(response)
        assert len(response["data"]["users"]["edges"]) == 1

    def test_user_creation_replicates_in_neodb(self, db, valid_user_payload):
        payload = valid_user_payload()
        # create a user in the db via graphql to trigger the replication signal
        graphql_query(queries.create_user, variables=payload)

        # get the user from postgres to check its uid
        response = graphql_query(queries.last_user).json()
        uid = response["data"]["users"]["edges"][0]["node"]["uid"]
        print(uid)

        # query neodb to verify the UserNode with this id exists
        user = UserNode.nodes.get_or_none(uid=uid)
        print(user)
        assert user is not None

    def test_user_can_follow(self, create_user_node):
        follower_token = create_user_node(token=True)
        # create other user to follow
        email = "bobby@bob.com"
        username = "my_boby"
        user = create_user_node(email=email, username=username)
        print(user)
        response = graphql_query(
            queries.follow_user,
            variables={"uid": str(user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {follower_token}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["followUser"]["user"]["uid"] == str(user["node"].uid)
        assert response["data"]["followUser"]["user"]["followersCount"] == 1
        assert response["data"]["followUser"]["user"]["email"] == email
        assert response["data"]["followUser"]["user"]["username"] == username

    def test_user_cannot_follow_twice(self, create_user_node):
        follower_token = create_user_node(token=True)
        # create other user to follow
        user = create_user_node()
        print(user)
        response1 = graphql_query(
            queries.follow_user,
            variables={"uid": str(user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {follower_token}"},
        ).json()
        print(response1)
        response2 = graphql_query(
            queries.follow_user,
            variables={"uid": str(user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {follower_token}"},
        ).json()
        print(response2)
        assert "errors" in response2
        assert response2["errors"][0]["message"] == USER_ALREADY_FOLLOWED_ERROR

    def test_user_cannot_follow_invalid_user(self, create_user_node):
        follower_token = create_user_node(token=True)
        invalid_user_uid = "1234"
        response = graphql_query(
            queries.follow_user,
            variables={"uid": invalid_user_uid},
            headers={"HTTP_AUTHORIZATION": f"JWT {follower_token}"},
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == USER_NOT_FOUND_ERROR
