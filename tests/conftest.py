from random import randint

import pytest
from graphene_django.utils.testing import graphql_query
from neomodel import db
from pytest_factoryboy import register

import tests.queries as queries
from accounts.models import User
from api.models import CommentNode, ReTweetNode, TweetNode
from tests.factories import UserFactory


@pytest.fixture(autouse=True, scope="session")
def setup_neo_test_db():
    print("Initializing test session fixture !")
    db.begin()
    yield
    print("Tear down session !")
    db.rollback()


register(UserFactory)


@pytest.fixture
def create_user(db, user_factory):
    user = user_factory.create()
    return user


@pytest.fixture
def valid_user_payload(faker):
    def make_valid_user_payload():
        password = faker.password(length=10)
        payload = {
            "email": faker.email(),
            "username": faker.first_name(),
            "password1": password,
            "password2": password,
        }
        return payload

    return make_valid_user_payload


@pytest.fixture
def create_user_node(valid_user_payload):
    def make_user_node(verified=False):
        response = graphql_query(queries.create_user, variables=valid_user_payload()).json()

        if verified:
            # get the user from postgres to check its uid
            res = graphql_query(queries.last_user).json()
            uid = res["data"]["users"]["edges"][0]["node"]["uid"]
            user = User.objects.get(uid=uid)

            # change the user status to verified
            user.status.verified = True
            user.status.save()
        return response["data"]["register"]

    return make_user_node


@pytest.fixture
@pytest.mark.django_db
def create_tweet_node(faker):
    def make_tweet_node(
        content=faker.sentence(),
        likes=randint(0, 100),
        retweets=randint(0, 100),
        comments=randint(0, 100),
    ):
        tweet = TweetNode(
            content=content,
            likes=likes,
            retweets=retweets,
            comments=comments,
        ).save()
        return tweet

    return make_tweet_node


@pytest.fixture
@pytest.mark.django_db
def create_likeable_node(faker):
    """
    params:
        type: String The type of likeable (TweetType, CommentType, ReTweetType)
    """

    def choose_maker(
        type,
        likes=randint(0, 100),
        content=faker.sentence(),
        retweets=randint(0, 100),
        comments=randint(0, 100),
    ):
        def make_tweet_node():
            tweet = TweetNode(
                likes=likes,
                content=content,
                comments=comments,
                retweets=retweets,
            ).save()
            return tweet

        def make_retweet_node():
            retweet = ReTweetNode(
                likes=likes,
                comments=comments,
            ).save()
            return retweet

        def make_comment_node():
            comment = CommentNode(
                likes=likes,
                content=content,
            ).save()
            return comment

        if type == "TweetType":
            return make_tweet_node()
        elif type == "ReTweetType":
            return make_retweet_node()
        else:
            return make_comment_node()

    return choose_maker
