import pytest
import tests.queries as queries
from _pytest.mark import param
from accounts.exceptions import LOGIN_REQUIRED_ERROR_MSG, NOT_VERIFIED_ACCOUNT_ERROR_MSG
from graphene_django.utils.testing import graphql_query

from api.errors import (
    ALREADY_LIKED_ERROR,
    COMMENT_EMPTY_ERROR,
    NOT_COMMENTABLE,
    NOT_LIKEABLE,
    TWEET_EMPTY_ERROR,
    TWEET_NOT_FOUND_ERROR,
)


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
            assert response["data"]["createTweet"]["tweet"]["retweets"] == 0
        else:
            assert response["errors"][0]["message"] == TWEET_EMPTY_ERROR

    def test_unauthenticated_user_cannot_like(self, create_tweet_node):
        tweet = create_tweet_node()
        variables = {"uid": tweet.uid, "type": "TweetType"}
        response = graphql_query(
            queries.create_like,
            variables=variables,
        ).json()
        print(response)
        assert response["errors"][0]["message"] == LOGIN_REQUIRED_ERROR_MSG

    @pytest.mark.parametrize(
        ["type"],
        [
            pytest.param("TweetType", id="TweetType"),
            pytest.param("ReTweetType", id="ReTweetType"),
            pytest.param("CommentType", id="CommentType"),
        ],
    )
    def test_authenticated_user_can_like(self, type, create_user_node, create_node):
        nb_likes = 99
        likeable = create_node(type, likes=nb_likes)
        print(f"likeable {likeable}")
        query_variables = {"uid": likeable.uid, "type": type}
        print(f"query vars {query_variables}")
        user_token = create_user_node()["token"]
        response = graphql_query(
            queries.create_like,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(f"response {response}")
        assert "errors" not in response
        assert response["data"]["createLike"]["likeable"]["uid"] == likeable.uid
        assert response["data"]["createLike"]["likeable"]["likes"] == nb_likes + 1
        assert response["data"]["createLike"]["likeable"]["__typename"] == type

    def test_cannot_like_nonexisting_tweet(self, create_user_node):
        not_proper_tweet_uid = 51
        query_variables = {"uid": not_proper_tweet_uid, "type": "TweetType"}
        user_token = create_user_node()["token"]
        response = graphql_query(
            queries.create_like,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        assert "errors" in response
        assert response["errors"][0]["message"] == NOT_LIKEABLE

    def test_cannot_like_badtypes(self, create_user_node, create_tweet_node):
        tweet = create_tweet_node()
        query_variables = {"uid": tweet.uid, "type": "BadType"}
        user_token = create_user_node()["token"]
        response = graphql_query(
            queries.create_like,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        assert "errors" in response
        assert response["errors"][0]["message"] == NOT_LIKEABLE

    def test_cannot_like_twice(self, create_user_node, create_node):
        """
        A user can make multiple tweets, but not on same likeable
        A likeable can be liked multiple times, but not by the same user
        """
        type = "TweetType"
        tweet = create_node(type)
        query_variables = {"uid": tweet.uid, "type": type}
        user_token = create_user_node()["token"]
        response1 = graphql_query(
            queries.create_like,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        response2 = graphql_query(
            queries.create_like,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response1)
        assert "errors" not in response1
        print(response2)
        assert "errors" in response2
        assert response2["errors"][0]["message"] == ALREADY_LIKED_ERROR

    def test_unauthenticated_user_cannot_comment(self, faker, create_tweet_node):
        tweet = create_tweet_node()
        content = faker.sentence()
        comment_variables = {"uid": tweet.uid, "type": "TweetType", "content": content}
        response = graphql_query(queries.create_comment, variables=comment_variables).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == LOGIN_REQUIRED_ERROR_MSG

    def test_unverified_user_cannot_comment(self, faker, create_user_node, create_tweet_node):
        user_token = create_user_node()["token"]
        tweet = create_tweet_node()
        content = faker.sentence()
        comment_variables = {"uid": tweet.uid, "type": "TweetType", "content": content}
        response = graphql_query(
            queries.create_comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        assert "errors" in response
        assert response["errors"][0]["message"] == NOT_VERIFIED_ACCOUNT_ERROR_MSG

    @pytest.mark.parametrize(
        "type",
        [
            pytest.param("TweetType", id="tweets"),
            pytest.param("ReTweetType", id="retweets"),
        ],
    )
    def test_verified_user_can_comment(self, faker, create_user_node, create_node, type):
        user_token = create_user_node(verified=True)["token"]
        nb_comments = 19
        commentable = create_node(type, comments=nb_comments)
        content = faker.sentence()
        comment_variables = {"uid": commentable.uid, "type": type, "content": content}
        response = graphql_query(
            queries.create_comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["createComment"]["commentable"]["uid"] == commentable.uid
        assert response["data"]["createComment"]["commentable"]["commentsList"][0]["content"] == content
        assert response["data"]["createComment"]["commentable"]["comments"] == nb_comments + 1

    def test_comment_cannot_be_empty(self, create_user_node, create_tweet_node):
        user_token = create_user_node(verified=True)["token"]
        tweet = create_tweet_node()
        content = ""
        comment_variables = {"content": content, "uid": tweet.uid, "type": "TweetType"}
        response = graphql_query(
            queries.create_comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == COMMENT_EMPTY_ERROR

    def test_comment_must_reference_commentable(self, faker, create_user_node):
        user_token = create_user_node(verified=True)["token"]
        invalid_tweet_uid = "123"
        content = faker.sentence()
        comment_variables = {"content": content, "uid": invalid_tweet_uid, "type": "TweetType"}
        response = graphql_query(
            queries.create_comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == NOT_COMMENTABLE

    def test_authenticated_user_can_retweet(self, create_user_node, create_tweet_node):
        user_token = create_user_node()["token"]
        tweet_node = create_tweet_node()
        retweet_variables = {"tweetUid": tweet_node.uid}
        response = graphql_query(
            queries.create_retweet,
            variables=retweet_variables,
            headers={
                "HTTP_AUTHORIZATION": f"JWT {user_token}",
            },
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["createRetweet"]["retweet"]["tweet"]["uid"] == tweet_node.uid
        assert response["data"]["createRetweet"]["retweet"]["tweet"]["retweets"] == tweet_node.retweets + 1

    def test_retweet_reference_must_exist(self, create_user_node):
        user_token = create_user_node()["token"]
        invalid_tweet_uid = "1234"
        retweet_variables = {"tweetUid": invalid_tweet_uid}
        response = graphql_query(
            queries.create_retweet,
            variables=retweet_variables,
            headers={
                "HTTP_AUTHORIZATION": f"JWT {user_token}",
            },
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == TWEET_NOT_FOUND_ERROR
