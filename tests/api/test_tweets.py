import pytest
import tests.queries as queries
from accounts.exceptions import LOGIN_REQUIRED_ERROR_MSG, NOT_VERIFIED_ACCOUNT_ERROR_MSG
from accounts.models import User
from graphene_django.utils.testing import graphql_query

from api.errors import TWEET_NOT_FOUND_ERROR


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

    def test_unauthenticated_user_cannot_like(self, create_tweet_node):
        tweet = create_tweet_node()
        variables = {"tweetUid": tweet.uid}
        response = graphql_query(
            queries.like_tweet,
            variables=variables,
        ).json()
        print(response)
        assert response["errors"][0]["message"] == LOGIN_REQUIRED_ERROR_MSG

    def test_authenticated_user_can_like(self, create_user_node, create_tweet_node):
        nb_likes = 99
        tweet = create_tweet_node(likes=nb_likes)
        query_variables = {"tweetUid": tweet.uid}
        user_token = create_user_node()["token"]
        response = graphql_query(
            queries.like_tweet,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["createLike"]["tweet"]["uid"] == tweet.uid
        assert response["data"]["createLike"]["tweet"]["likes"] == nb_likes + 1

    def test_cannot_like_nonexisting_tweet(self, create_user_node):
        not_proper_tweet_uid = 51
        query_variables = {"tweetUid": not_proper_tweet_uid}
        user_token = create_user_node()["token"]
        response = graphql_query(
            queries.like_tweet,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        assert "errors" in response
        assert response["errors"][0]["message"] == TWEET_NOT_FOUND_ERROR
