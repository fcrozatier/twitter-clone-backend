import graphene
from accounts.decorators import login_required, user_verified
from graphene.types.objecttype import ObjectType

from api.errors import TWEET_NOT_FOUND_ERROR
from api.models import TweetNode, UserNode


class TweetType(graphene.ObjectType):
    uid = graphene.String(required=True)
    content = graphene.String(required=True)
    likes = graphene.Int()
    created = graphene.DateTime()

    def resolve_uid(parent, info):
        return parent.uid

    def resolve_content(parent, info):
        return parent.content

    def resolve_likes(parent, info):
        return parent.likes


class CreateTweet(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)

    tweet = graphene.Field(TweetType)

    @login_required
    @user_verified
    def mutate(parent, info, content):
        user_uid = info.context.user.uid
        tweet = TweetNode(content=content).save()
        user = UserNode.nodes.get(uid=user_uid)
        user.tweets.connect(tweet)
        return CreateTweet(tweet=tweet)


class CreateLike(graphene.Mutation):
    class Arguments:
        tweet_uid = graphene.String(required=True)

    tweet = graphene.Field(TweetType)

    @login_required
    def mutate(parent, info, tweet_uid):
        user_uid = info.context.user.uid
        tweet = TweetNode.nodes.get_or_none(uid=tweet_uid)
        if not tweet:
            raise Exception(TWEET_NOT_FOUND_ERROR)
        tweet.likes += 1
        tweet.save()
        user = UserNode.nodes.get(uid=user_uid)
        user.likes.connect(tweet)
        return CreateLike(tweet=tweet)


class Query(graphene.ObjectType):
    tweets = graphene.List(TweetType)

    def resolve_tweets(root, info, **kwargs):
        return TweetNode.nodes.all()


class Mutation(ObjectType):
    create_tweet = CreateTweet.Field()
    create_like = CreateLike.Field()
