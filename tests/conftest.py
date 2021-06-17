from random import randint

import pytest
from graphene_django.utils.testing import graphql_query
from neomodel import db as neodb
from pytest_factoryboy import register

import tests.queries as queries
from accounts.models import User
from api.models import CommentNode, ReTweetNode, TweetNode
from tests.factories import UserFactory

register(UserFactory)


@pytest.fixture(autouse=True, scope="session")
def setup_neo_test_db():
    neodb.begin()
    yield
    neodb.rollback()


@pytest.fixture
def valid_user_payload(faker):
    # Call faker in the body and not the params to be able to create multiple distinct user in the same test
    def make_valid_user_payload(email=None, username=None):
        password = faker.password(length=10)
        payload = {
            "email": email or faker.email(),
            "username": username or faker.first_name(),
            "password1": password,
            "password2": password,
        }
        return payload

    return make_valid_user_payload


@pytest.fixture
def create_user_node(valid_user_payload):
    """
    Fixture to create a user in postgres db and neodb
    Params:
        username / email for a custom user
        verified if you want a verified user
        token returns the user token
        response returns the base response
            token has precedence over response
    Returns the user created
    """

    def make_user_node(verified=False, token=False, response=False, **kwargs):
        rsponse = graphql_query(queries.create_user, variables=valid_user_payload(**kwargs)).json()

        # get the user from postgres to check its uid
        res = graphql_query(queries.last_user).json()
        uid = res["data"]["users"]["edges"][0]["node"]["uid"]
        user = User.objects.get(uid=uid)

        if verified:
            # change the user status to verified
            user.status.verified = True
            user.status.save()

        if response:
            return rsponse

        tken = rsponse["data"]["register"]["token"]
        if token:
            return tken

        return {"node": user, "token": tken}

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
def create_node(faker):
    """
    Creates a node of a given type
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
