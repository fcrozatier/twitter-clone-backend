import pytest
from api.errors import GENERIC_ERROR
from graphene_django.utils.testing import graphql_query
from tests import queries


@pytest.mark.django_db
class TestProfile:
    def test_user_can_query_my_profile(self, create_user_node):
        username = "JJ"
        email = "j@j.com"
        user_token = create_user_node(token=True, username=username, email=email)
        response = graphql_query(
            queries.my_profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user_token}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["myProfile"]["username"] == username
        assert response["data"]["myProfile"]["email"] == email
        assert response["data"]["myProfile"]["followersCount"] == 0
        assert response["data"]["myProfile"]["tweets"] == []
        assert response["data"]["myProfile"]["likes"] == []

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
            queries.my_profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["myProfile"]["followersCount"] == 1

    def test_profile_updates_with_tweets(self, create_user_node, create_node):
        user = create_user_node(verified=True)
        type = "TweetType"
        tweet_node = create_node(type)

        res_create_content = graphql_query(
            queries.tweet,
            variables={"content": tweet_node.content},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        assert "errors" not in res_create_content

        response = graphql_query(
            queries.my_profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["myProfile"]["tweets"] != []
        assert response["data"]["myProfile"]["tweets"][0]["content"] == tweet_node.content

    def test_profile_update_with_retweets(self, create_user_node, create_node):
        user = create_user_node(verified=True)
        tweet_node = create_node("TweetType")

        res_create_content = graphql_query(
            queries.create_retweet,
            variables={"tweetUid": tweet_node.uid},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        assert "errors" not in res_create_content

        response = graphql_query(
            queries.my_profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["myProfile"]["retweets"] != []
        assert response["data"]["myProfile"]["retweets"][0]["tweet"]["uid"] == tweet_node.uid

    @pytest.mark.parametrize(
        "type",
        [
            pytest.param("TweetType", id="tweet"),
            pytest.param("ReTweetType", id="retweet"),
        ],
    )
    def test_profile_updates_with_comments(self, create_user_node, create_node, faker, type):
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
            queries.my_profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in response
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
    def test_profile_updates_with_likes(self, create_user_node, create_node, type):
        user = create_user_node(verified=True)
        content_node = create_node(type)

        res_create_content = graphql_query(
            queries.like,
            variables={"uid": content_node.uid, "type": type},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        assert "errors" not in res_create_content

        response = graphql_query(
            queries.my_profile,
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["myProfile"]["likes"] != []
        assert response["data"]["myProfile"]["likes"][0]["__typename"] == type
        assert response["data"]["myProfile"]["likes"][0]["uid"] == content_node.uid

    def test_my_followers(self, create_user_node):
        user = create_user_node()

        for i in range(0, 10):
            follower = create_user_node(username=f"follower__{i}")

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
        assert "errors" not in response
        assert response["data"]["myProfile"]["followers"] != []
        assert len(response["data"]["myProfile"]["followers"]) == 10
        assert response["data"]["myProfile"]["followers"][0]["username"] == "follower__9"

        response = graphql_query(
            queries.my_followers,
            variables={"first": 3, "skip": 2},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["myProfile"]["followers"] != []
        assert len(response["data"]["myProfile"]["followers"]) == 3
        assert response["data"]["myProfile"]["followers"][0]["username"] == "follower__7"

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
        assert "errors" not in response
        assert response["data"]["myProfile"]["follows"] != []
        assert response["data"]["myProfile"]["follows"][0]["uid"] == str(followed_user["node"].uid)
        assert response["data"]["myProfile"]["follows"][0]["email"] == (followed_user["node"].email)

    def test_user_profile(self, create_user_node):
        my_token = create_user_node(token=True)
        username = "JJ"
        email = "j@j.com"
        user_node = create_user_node(username=username, email=email)
        variables = {"uid": str(user_node["node"].uid)}
        response = graphql_query(
            queries.user_profile,
            variables=variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {my_token}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["userProfile"]["username"] == username
        assert response["data"]["userProfile"]["email"] == email
        assert response["data"]["userProfile"]["followersCount"] == 0
        assert response["data"]["userProfile"]["tweets"] == []

    def test_bad_user_profile(self, create_user_node):
        my_token = create_user_node(token=True)
        bad_user_uid = "1234"
        variables = {"uid": bad_user_uid}
        response = graphql_query(
            queries.user_profile,
            variables=variables,
            headers={"HTTP_AUTHORIZATION": f"JWT {my_token}"},
        ).json()
        print(response)
        assert "errors" in response
        assert response["errors"][0]["message"] == GENERIC_ERROR

    def test_user_followers(self, create_user_node):
        my_token = create_user_node(token=True)
        user = create_user_node()
        follower = create_user_node()

        res_add_follower = graphql_query(
            queries.follow_user,
            variables={"uid": str(user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {follower['token']}"},
        ).json()
        assert "errors" not in res_add_follower

        response = graphql_query(
            queries.user_followers,
            variables={"uid": str(user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {my_token}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["userProfile"]["followers"] != []
        assert response["data"]["userProfile"]["followers"][0]["uid"] == str(follower["node"].uid)
        assert response["data"]["userProfile"]["followers"][0]["email"] == (follower["node"].email)

    def test_user_subs(self, create_user_node):
        my_token = create_user_node(token=True)
        user = create_user_node()
        followed_user = create_user_node()

        res_add_follower = graphql_query(
            queries.follow_user,
            variables={"uid": str(followed_user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {user['token']}"},
        ).json()
        assert "errors" not in res_add_follower

        response = graphql_query(
            queries.user_subs,
            variables={"uid": str(user["node"].uid)},
            headers={"HTTP_AUTHORIZATION": f"JWT {my_token}"},
        ).json()
        print(response)
        assert "errors" not in response
        assert response["data"]["userProfile"]["follows"] != []
        assert response["data"]["userProfile"]["follows"][0]["uid"] == str(followed_user["node"].uid)
        assert response["data"]["userProfile"]["follows"][0]["email"] == (followed_user["node"].email)
