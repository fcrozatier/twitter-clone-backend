import pytest
import tests.queries as queries
from _pytest.main import pytest_collection_modifyitems
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
        pass
