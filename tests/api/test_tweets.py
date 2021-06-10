import pytest
import tests.queries as queries
from accounts.exceptions import LOGIN_REQUIRED_ERROR_MSG, NOT_VERIFIED_ACCOUNT_ERROR_MSG
from graphene_django.utils.testing import graphql_query

from api.errors import COMMENT_EMPTY_ERROR, TWEET_EMPTY_ERROR, TWEET_NOT_FOUND_ERROR


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

    @pytest.mark.parametrize(
        ["tweet_content", "validity"],
        [
            pytest.param("test tweet", True, id="Nonempty tweet is valid"),
            pytest.param("", False, id="Empty tweet is not valid"),
        ],
    )
    def test_verified_user_can_tweet(self, create_user_node, tweet_content, validity):
        token = create_user_node(verified=True)["token"]

        # login and make a tweet
        variables = {"content": tweet_content}
        response = graphql_query(
            queries.create_tweet,
            variables=variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {token}"},
        ).json()
        print(response)
        if validity:
            assert response["data"]["createTweet"]["tweet"]["content"] == tweet_content
            assert response["data"]["createTweet"]["tweet"]["likes"] == 0
            assert response["data"]["createTweet"]["tweet"]["comments"] == 0
        else:
            assert response["errors"][0]["message"] == TWEET_EMPTY_ERROR

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

    def test_unauthenticated_user_cannot_comment(self, faker, create_tweet_node):
        tweet = create_tweet_node()
        content = faker.sentence()
        comment_variables = {"content": content, "tweetUid": tweet.uid}
        response = graphql_query(queries.create_comment, variables=comment_variables).json()
        assert "errors" in response
        assert response["errors"][0]["message"] == LOGIN_REQUIRED_ERROR_MSG

    def test_unverified_user_cannot_comment(self, faker, create_user_node, create_tweet_node):
        user_token = create_user_node()["token"]
        tweet = create_tweet_node()
        content = faker.sentence()
        comment_variables = {"content": content, "tweetUid": tweet.uid}
        response = graphql_query(
            queries.create_comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        assert "errors" in response
        assert response["errors"][0]["message"] == NOT_VERIFIED_ACCOUNT_ERROR_MSG

    def test_verified_user_can_comment(self, faker, create_user_node, create_tweet_node):
        user_token = create_user_node(verified=True)["token"]
        nb_comments = 19
        tweet = create_tweet_node(comments=nb_comments)
        content = faker.sentence()
        comment_variables = {"content": content, "tweetUid": tweet.uid}
        response = graphql_query(
            queries.create_comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["createComment"]["comment"]["content"] == content
        assert response["data"]["createComment"]["comment"]["content"] == content
        assert response["data"]["createComment"]["comment"]["tweet"]["uid"] == tweet.uid
        assert response["data"]["createComment"]["comment"]["tweet"]["comments"] == nb_comments + 1

    def test_comment_cannot_be_empty(self, create_user_node, create_tweet_node):
        user_token = create_user_node(verified=True)["token"]
        tweet = create_tweet_node()
        content = ""
        comment_variables = {"content": content, "tweetUid": tweet.uid}
        response = graphql_query(
            queries.create_comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == COMMENT_EMPTY_ERROR

    def test_comment_must_reference_tweet(self, faker, create_user_node):
        user_token = create_user_node(verified=True)["token"]
        invalid_tweet_uid = "123"
        content = faker.sentence()
        comment_variables = {"content": content, "tweetUid": invalid_tweet_uid}
        response = graphql_query(
            queries.create_comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == TWEET_NOT_FOUND_ERROR
