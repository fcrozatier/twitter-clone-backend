import pytest
import tests.queries as queries
from accounts.exceptions import LOGIN_REQUIRED_ERROR_MSG, NOT_VERIFIED_ACCOUNT_ERROR_MSG
from accounts.models import User
from graphene_django.utils.testing import graphql_query


@pytest.mark.django_db
class TestTweets:
    def test_unauthenticated_user_cannot_tweet(self):
        variables = {"content": "test tweet"}
        response = graphql_query(queries.create_tweet, variables=variables).json()
        print(response)
        assert response["errors"][0]["message"] == LOGIN_REQUIRED_ERROR_MSG

    def test_unverified_user_cannot_tweet(self, create_user_node):
        token = create_user_node()["token"]
        variables = {"content": "test tweet"}
        response = graphql_query(
            queries.create_tweet,
            variables=variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {token}"},
        ).json()
        print(response)
        assert response["errors"][0]["message"] == NOT_VERIFIED_ACCOUNT_ERROR_MSG

    def test_verified_user_can_tweet(self, create_user_node):
        token = create_user_node()["token"]

        # get the user from postgres to check its uid
        response = graphql_query(queries.last_user).json()
        uid = response["data"]["users"]["edges"][0]["node"]["uid"]
        user = User.objects.get(uid=uid)

        # change the user status to verified
        user.status.verified = True
        user.status.save()

        # login and make a tweet
        variables = {"content": "test tweet"}
        response = graphql_query(
            queries.create_tweet,
            variables=variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {token}"},
        ).json()
        print(response)
        assert "createTweet" in response["data"]
