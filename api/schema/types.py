import graphene
from api.schema.decorators import add_base_resolvers
from graphene.types.objecttype import ObjectType


class LikeableType(graphene.Interface):
    uid = graphene.String(required=True)
    likes = graphene.Int()
    created = graphene.DateTime()

    @classmethod
    def resolve_type(cls, instance, info):
        """
        We know instance is a likeable node since this method is only called after a CreateLike mutation.
        """
        node_class_name = instance.__class__.__name__
        type_class_name = node_class_name.replace("Node", "Type")
        return globals()[type_class_name]


@add_base_resolvers
class CommentType(ObjectType):
    class Meta:
        interfaces = (LikeableType,)

    content = graphene.String(required=True)


class CommentableType(graphene.Interface):
    comments = graphene.Int()
    comments_list = graphene.List(CommentType)

    @classmethod
    def resolve_type(cls, instance, info):
        node_class_name = instance.__class__.__name__
        type_class_name = node_class_name.replace("Node", "Type")
        return globals()[type_class_name]


@add_base_resolvers
class TweetType(graphene.ObjectType):
    class Meta:
        interfaces = (LikeableType, CommentableType)

    content = graphene.String(required=True)
    retweets = graphene.Int()

    def resolve_comments_list(parent, info):
        return parent.commented.all()


@add_base_resolvers
class ReTweetType(ObjectType):
    class Meta:
        interfaces = (LikeableType, CommentableType)

    tweet = graphene.Field(TweetType)

    def resolve_tweet(parent, info):
        return parent.tweet.single()

    def resolve_comments_list(parent, info):
        return parent.commented.all()
