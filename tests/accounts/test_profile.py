import pytest
from graphene_django.utils.testing import graphql_query
from tests import queries


@pytest.mark.django_db
class TestProfile:
    def test_user_can_query_profile(self, create_user_node):
        username = "JJ"
        email = "j@j.com"
        user_token = create_user_node(token=True, username=username, email=email)
        response = graphql_query(
            queries.profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" not in "response"
        assert response["data"]["myProfile"]["username"] == username
        assert response["data"]["myProfile"]["email"] == email
        assert response["data"]["myProfile"]["followersCount"] == 0
        assert response["data"]["myProfile"]["tweets"] == []

    def test_profile_updates_with_followers(self, create_user_node):
        user = create_user_node()
        follower = create_user_node()

        res_add_follower = graphql_query(
            queries.follow_user,
            variables={"uid": str(user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {follower['token']}"},
        ).json()
        assert "errors" not in res_add_follower

        response = graphql_query(
            queries.profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in "response"
        assert response["data"]["myProfile"]["followersCount"] == 1

    def test_profile_tweets(self, create_user_node, create_node):
        user = create_user_node(verified=True)
        type = "TweetType"
        tweet_node = create_node(type)

        res_create_content = graphql_query(
            queries.create_tweet,
            variables={"content": tweet_node.content},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        assert "errors" not in res_create_content

        response = graphql_query(
            queries.profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in "response"
        assert response["data"]["myProfile"]["tweets"] != []
        assert response["data"]["myProfile"]["tweets"][0]["content"] == tweet_node.content

    def test_profile_retweets(self, create_user_node, create_node):
        user = create_user_node(verified=True)
        tweet_node = create_node("TweetType")

        res_create_content = graphql_query(
            queries.create_retweet,
            variables={"tweetUid": tweet_node.uid},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        assert "errors" not in res_create_content

        response = graphql_query(
            queries.profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in "response"
        assert response["data"]["myProfile"]["retweets"] != []
        assert response["data"]["myProfile"]["retweets"][0]["tweet"]["uid"] == tweet_node.uid

    @pytest.mark.parametrize(
        "type",
        [
            pytest.param("TweetType", id="tweet"),
            pytest.param("ReTweetType", id="retweet"),
        ],
    )
    def test_profile_comments(self, create_user_node, create_node, faker, type):
        user = create_user_node(verified=True)
        content_node = create_node(type)
        comment = faker.sentence()

        res_create_content = graphql_query(
            queries.create_comment,
            variables={"uid": content_node.uid, "type": type, "content": comment},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        assert "errors" not in res_create_content

        response = graphql_query(
            queries.profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in "response"
        assert response["data"]["myProfile"]["comments"] != []
        assert response["data"]["myProfile"]["comments"][0]["content"] == comment

    @pytest.mark.parametrize(
        "type",
        [
            pytest.param("TweetType", id="tweet"),
            pytest.param("ReTweetType", id="retweet"),
            pytest.param("CommentType", id="comment"),
        ],
    )
    def test_profile_likes(self, create_user_node, create_node, type):
        user = create_user_node(verified=True)
        content_node = create_node(type)

        res_create_content = graphql_query(
            queries.create_like,
            variables={"uid": content_node.uid, "type": type},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        assert "errors" not in res_create_content

        response = graphql_query(
            queries.profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in "response"
        assert response["data"]["myProfile"]["likes"] != []
        assert response["data"]["myProfile"]["likes"][0]["__typename"] == type
        assert response["data"]["myProfile"]["likes"][0]["uid"] == content_node.uid

    def test_my_followers(self, create_user_node):
        user = create_user_node()
        follower = create_user_node()

        res_add_follower = graphql_query(
            queries.follow_user,
            variables={"uid": str(user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {follower['token']}"},
        ).json()
        assert "errors" not in res_add_follower

        response = graphql_query(
            queries.my_followers,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in "response"
        assert response["data"]["myFollowers"] != []
        assert response["data"]["myFollowers"][0]["uid"] == str(follower["node"].uid)
        assert response["data"]["myFollowers"][0]["email"] == (follower["node"].email)

    def test_my_subs(self, create_user_node):
        user = create_user_node()
        followed_user = create_user_node()

        res_add_follower = graphql_query(
            queries.follow_user,
            variables={"uid": str(followed_user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        assert "errors" not in res_add_follower

        response = graphql_query(
            queries.my_subs,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in "response"
        assert response["data"]["mySubs"] != []
        assert response["data"]["mySubs"][0]["uid"] == str(followed_user["node"].uid)
        assert response["data"]["mySubs"][0]["email"] == (followed_user["node"].email)
