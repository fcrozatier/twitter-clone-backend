import graphene
from accounts.models import User
from api.errors import GENERIC_ERROR
from api.models.models import CommentNode, ReTweetNode, TweetNode, UserNode
from graphene.types.objecttype import ObjectType


class GettableMixin:
    @classmethod
    def get_node(cls, uid):
        try:
            node = cls._get_node(uid=uid)
        except:
            raise Exception(GENERIC_ERROR)
        return node


class BaseDatedType(graphene.Interface):
    uid = graphene.String(required=True)
    created = graphene.DateTime()


class LikeableType(graphene.Interface):
    likes = graphene.Int()

    @classmethod
    def resolve_type(cls, instance, info):
        """
        We know instance is a likeable node since this method is only called after a CreateLike mutation.
        """
        node_class_name = instance.__class__.__name__
        type_class_name = node_class_name.replace("Node", "Type")
        return globals()[type_class_name]


class CommentType(GettableMixin, ObjectType):
    class Meta:
        interfaces = (LikeableType, BaseDatedType)

    content = graphene.String(required=True)

    @classmethod
    def _get_node(cls, uid):
        return CommentNode.nodes.get(uid=uid)


class CommentableType(graphene.Interface):
    comments = graphene.Int()
    comments_list = graphene.List(CommentType)

    @classmethod
    def resolve_type(cls, instance, info):
        node_class_name = instance.__class__.__name__
        type_class_name = node_class_name.replace("Node", "Type")
        return globals()[type_class_name]


class TweetType(GettableMixin, ObjectType):
    class Meta:
        interfaces = (LikeableType, CommentableType, BaseDatedType)

    content = graphene.String(required=True)
    retweets = graphene.Int()

    @classmethod
    def _get_node(cls, uid):
        return TweetNode.nodes.get(uid=uid)

    def resolve_comments_list(parent, info):
        return parent.commented.all()


class ReTweetType(GettableMixin, ObjectType):
    class Meta:
        interfaces = (LikeableType, CommentableType, BaseDatedType)

    tweet = graphene.Field(TweetType)

    @classmethod
    def _get_node(cls, uid):
        return ReTweetNode.nodes.get(uid=uid)

    def resolve_tweet(parent, info):
        return parent.tweet.single()

    def resolve_comments_list(parent, info):
        return parent.commented.all()


class UserType(GettableMixin, ObjectType):
    class Meta:
        interfaces = (BaseDatedType,)

    uid = graphene.String(required=True, source="uid")
    email = graphene.String()
    username = graphene.String()
    followers_count = graphene.Int(source="followers_count")
    tweets = graphene.List(TweetType)
    retweets = graphene.List(ReTweetType)
    comments = graphene.List(CommentType)
    likes = graphene.List(LikeableType)

    @classmethod
    def _get_node(cls, uid):
        return UserNode.nodes.get(uid=uid)

    def resolve_email(parent, info):
        return User.objects.get(uid=parent.uid).email

    def resolve_username(parent, info):
        return User.objects.get(uid=parent.uid).username

    def resolve_tweets(parent, info):
        return parent.tweets.all()

    def resolve_retweets(parent, info):
        return parent.retweets.all()

    def resolve_comments(parent, info):
        return parent.comments.all()

    def resolve_likes(parent, info):
        return parent.likes.all()
