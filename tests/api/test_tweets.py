import pytest
import tests.queries as queries
from accounts.exceptions import LOGIN_REQUIRED_ERROR_MSG, NOT_VERIFIED_ACCOUNT_ERROR_MSG
from graphene_django.utils.testing import graphql_query

from api.errors import (
    ALREADY_LIKED_ERROR,
    ALREADY_RETWEETED_ERROR,
    COMMENT_EMPTY_ERROR,
    COMMENT_NOT_FOUND_ERROR,
    NOT_COMMENTABLE,
    NOT_LIKEABLE,
    RETWEET_NOT_FOUND_ERROR,
    TWEET_EMPTY_ERROR,
    TWEET_NOT_FOUND_ERROR,
    UNLIKED_ERROR,
)


@pytest.mark.django_db
class TestTweets:
    def test_unauthenticated_user_cannot_tweet(self):
        variables = {"content": "test tweet"}
        response = graphql_query(queries.tweet, variables=variables).json()
        print(response)
        assert response["errors"][0]["message"] == LOGIN_REQUIRED_ERROR_MSG

    def test_unverified_user_cannot_tweet(self, create_user_node):
        token = create_user_node(token=True)
        variables = {"content": "test tweet"}
        response = graphql_query(
            queries.tweet,
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
        token = create_user_node(verified=True, token=True)

        # login and make a tweet
        variables = {"content": tweet_content}
        response = graphql_query(
            queries.tweet,
            variables=variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {token}"},
        ).json()
        print(response)
        if validity:
            assert response["data"]["tweet"]["content"] == tweet_content
            assert response["data"]["tweet"]["likes"] == 0
            assert response["data"]["tweet"]["comments"] == 0
            assert response["data"]["tweet"]["retweets"] == 0
        else:
            assert response["errors"][0]["message"] == TWEET_EMPTY_ERROR

    def test_tweets_order_filter(self, create_user_node):
        my_token = create_user_node(verified=True, token=True)

        # login and make tweets
        for i in range(0, 10):
            variables = {"content": f"tweet {i}"}
            graphql_query(
                queries.tweet,
                variables=variables,
                headers={"HTTP_AUTHORIZATION": f"JWT {my_token}"},
            ).json()

        response = graphql_query(
            queries.my_profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {my_token}"},
        ).json()

        print(response)

        assert len(response["data"]["myProfile"]["tweets"]) == 10
        assert response["data"]["myProfile"]["tweets"][0]["content"] == "tweet 9"
        assert response["data"]["myProfile"]["tweets"][9]["content"] == "tweet 0"

        response = graphql_query(
            """query {
                myProfile {
                    tweets(first:2, skip:2) {
                        created
                        content
                    }
                }
            }""",
            headers={"HTTP_AUTHORIZATION": f"JWT {my_token}"},
        ).json()

        print(response)

        assert len(response["data"]["myProfile"]["tweets"]) == 2
        assert response["data"]["myProfile"]["tweets"][0]["content"] == "tweet 7"
        assert response["data"]["myProfile"]["tweets"][1]["content"] == "tweet 6"

    def test_unauthenticated_user_cannot_like(self, create_tweet_node):
        tweet = create_tweet_node()
        variables = {"uid": tweet.uid, "type": "TweetType"}
        response = graphql_query(
            queries.like,
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
        user_token = create_user_node(token=True)
        response = graphql_query(
            queries.like,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(f"response {response}")
        assert "errors" not in response
        assert response["data"]["like"]["uid"] == likeable.uid
        assert response["data"]["like"]["likes"] == nb_likes + 1
        assert response["data"]["like"]["__typename"] == type

    @pytest.mark.parametrize(
        ["type", "error_msg"],
        [
            pytest.param("TweetType", TWEET_NOT_FOUND_ERROR, id="tweet"),
            pytest.param("ReTweetType", RETWEET_NOT_FOUND_ERROR, id="retweet"),
            pytest.param("CommentType", COMMENT_NOT_FOUND_ERROR, id="comment"),
        ],
    )
    def test_cannot_like_nonexisting_likeable(self, create_user_node, type, error_msg):
        user_token = create_user_node(token=True)

        not_proper_uid = "1234"
        query_variables = {"uid": not_proper_uid, "type": type}

        response = graphql_query(
            queries.like,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        assert "errors" in response
        assert response["errors"][0]["message"] == error_msg

    @pytest.mark.parametrize(
        "type",
        [
            pytest.param("BadType", id="Nonexisting type"),
            pytest.param("UserType", id="Nonlikeable type"),
        ],
    )
    def test_cannot_like_badtypes(self, create_user_node, create_tweet_node, type):
        tweet = create_tweet_node()
        query_variables = {"uid": tweet.uid, "type": type}
        user_token = create_user_node(token=True)
        response = graphql_query(
            queries.like,
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
        user_token = create_user_node(token=True)
        response1 = graphql_query(
            queries.like,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        response2 = graphql_query(
            queries.like,
            variables=query_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response1)
        assert "errors" not in response1
        print(response2)
        assert "errors" in response2
        assert response2["errors"][0]["message"] == ALREADY_LIKED_ERROR

    @pytest.mark.parametrize(
        ["type", "valid"],
        [
            pytest.param("TweetType", True, id="tweet"),
            pytest.param("UserType", False, id="not likeable"),
            pytest.param("BadType", False, id="not type"),
        ],
    )
    def test_unlike(self, create_user_node, create_node, type, valid):
        nb_likes = 99
        likeable = create_node("TweetType", likes=nb_likes)

        like_variables = {"uid": likeable.uid, "type": "TweetType"}
        user_token = create_user_node(token=True)
        response = graphql_query(
            queries.like,
            variables=like_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(f"response {response}")
        assert "errors" not in response
        assert response["data"]["like"]["likes"] == nb_likes + 1

        unlike_variables = {"uid": likeable.uid, "type": type}
        response = graphql_query(
            queries.unlike,
            variables=unlike_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(f"response {response}")
        if valid:
            assert "errors" not in response
            assert response["data"]["unlike"]["uid"] == likeable.uid
            assert response["data"]["unlike"]["likes"] == nb_likes
            assert response["data"]["unlike"]["__typename"] == type
        else:
            assert "errors" in response
            assert response["errors"][0]["message"] == UNLIKED_ERROR

    def test_user_must_like_before_unlike(self, create_user_node, create_node):
        type = "CommentType"
        tweet = create_node(type, likes=99)
        user_token = create_user_node(token=True)
        variables = {"uid": tweet.uid, "type": type}

        response = graphql_query(
            queries.unlike, variables=variables, headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"}
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == UNLIKED_ERROR

    def test_unauthenticated_user_cannot_comment(self, faker, create_tweet_node):
        tweet = create_tweet_node()
        content = faker.sentence()
        comment_variables = {"uid": tweet.uid, "type": "TweetType", "content": content}
        response = graphql_query(queries.comment, variables=comment_variables).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == LOGIN_REQUIRED_ERROR_MSG

    def test_unverified_user_cannot_comment(self, faker, create_user_node, create_tweet_node):
        user_token = create_user_node(token=True)
        tweet = create_tweet_node()
        content = faker.sentence()
        comment_variables = {"uid": tweet.uid, "type": "TweetType", "content": content}
        response = graphql_query(
            queries.comment,
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
        user_token = create_user_node(verified=True, token=True)
        nb_comments = 19
        commentable = create_node(type, comments=nb_comments)
        content = faker.sentence()
        comment_variables = {"uid": commentable.uid, "type": type, "content": content}
        response = graphql_query(
            queries.comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["comment"]["about"]["__typename"] == type
        assert response["data"]["comment"]["about"]["uid"] == commentable.uid
        assert response["data"]["comment"]["about"]["commentsList"][0]["content"] == content
        assert response["data"]["comment"]["about"]["comments"] == nb_comments + 1

    def test_comment_cannot_be_empty(self, create_user_node, create_tweet_node):
        user_token = create_user_node(verified=True, token=True)
        tweet = create_tweet_node()
        content = ""
        comment_variables = {"content": content, "uid": tweet.uid, "type": "TweetType"}
        response = graphql_query(
            queries.comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == COMMENT_EMPTY_ERROR

    @pytest.mark.parametrize(
        ["type", "error_msg"],
        [
            pytest.param("TweetType", TWEET_NOT_FOUND_ERROR, id="Bad uid"),
            pytest.param("UserType", NOT_COMMENTABLE, id="Bad type"),
            pytest.param("BadType", NOT_COMMENTABLE, id="Non-existing type"),
        ],
    )
    def test_comment_must_reference_commentable(self, faker, create_user_node, type, error_msg):
        user_token = create_user_node(verified=True, token=True)
        invalid_tweet_uid = "123"
        content = faker.sentence()
        comment_variables = {"content": content, "uid": invalid_tweet_uid, "type": type}
        response = graphql_query(
            queries.comment,
            variables=comment_variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == error_msg

    def test_authenticated_user_can_retweet(self, create_user_node, create_tweet_node):
        user_token = create_user_node(token=True)
        tweet_node = create_tweet_node()
        retweet_variables = {"uid": tweet_node.uid}
        response = graphql_query(
            queries.retweet,
            variables=retweet_variables,
            headers={
                "HTTP_AUTHORIZATION": f"JWT {user_token}",
            },
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["retweet"]["tweet"]["uid"] == tweet_node.uid
        assert response["data"]["retweet"]["tweet"]["retweets"] == tweet_node.retweets + 1

    def test_cannot_retweet_twice(self, create_user_node, create_tweet_node):
        user_token = create_user_node(token=True)
        tweet_node = create_tweet_node()
        retweet_variables = {"uid": tweet_node.uid}
        response = graphql_query(
            queries.retweet,
            variables=retweet_variables,
            headers={
                "HTTP_AUTHORIZATION": f"JWT {user_token}",
            },
        ).json()
        print(response)
        assert "errors" not in response

        response = graphql_query(
            queries.retweet,
            variables=retweet_variables,
            headers={
                "HTTP_AUTHORIZATION": f"JWT {user_token}",
            },
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == ALREADY_RETWEETED_ERROR

    def test_retweet_reference_must_exist(self, create_user_node):
        user_token = create_user_node(token=True)
        invalid_tweet_uid = "1234"
        retweet_variables = {"uid": invalid_tweet_uid}
        response = graphql_query(
            queries.retweet,
            variables=retweet_variables,
            headers={
                "HTTP_AUTHORIZATION": f"JWT {user_token}",
            },
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == TWEET_NOT_FOUND_ERROR
