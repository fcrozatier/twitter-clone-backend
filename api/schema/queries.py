import graphene
from api.models import TweetNode
from api.schema.types import TweetType


class Query(graphene.ObjectType):
    tweets = graphene.List(TweetType)

    def resolve_tweets(root, info, **kwargs):
        return TweetNode.nodes.all()
