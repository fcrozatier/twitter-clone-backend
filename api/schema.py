import graphene
from accounts.decorators import login_required, user_verified
from graphene.types.objecttype import ObjectType

from api.models import Tweet, UserNode


class TweetType(graphene.ObjectType):
    content = graphene.String(required=True)
    created = graphene.DateTime()

    def resolve_content(parent, info):
        return parent.content


class CreateTweet(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)

    tweet = graphene.Field(TweetType)

    @login_required
    @user_verified
    def mutate(parent, info, content):
        uid = info.context.user.uid
        tweet = Tweet(content=content).save()
        user = UserNode.nodes.get(uid=uid)
        user.tweets.connect(tweet)
        return CreateTweet(tweet=tweet)


class Query(graphene.ObjectType):
    tweets = graphene.List(TweetType)

    def resolve_tweets(root, info, **kwargs):
        return Tweet.nodes.all()


class Mutation(ObjectType):
    create_tweet = CreateTweet.Field()
