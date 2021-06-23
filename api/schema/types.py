import graphene
from accounts.models import User
from api.errors import (
    COMMENT_NOT_FOUND_ERROR,
    RETWEET_NOT_FOUND_ERROR,
    TWEET_NOT_FOUND_ERROR,
    USER_NOT_FOUND_ERROR,
)
from api.models.models import CommentNode, ReTweetNode, TweetNode, UserNode
from api.schema.loaders import UserLoader
from graphene.types.objecttype import ObjectType

user_loader = UserLoader()


class GettableMixin:
    @classmethod
    def get_node(cls, uid):
        try:
            node = cls._get_node(uid=uid)
        except:
            raise cls._get_error()
        return node

    @staticmethod
    def filter_qs(qs, first, skip):
        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        return qs


class BaseDatedType(graphene.Interface):
    uid = graphene.String(required=True)
    created = graphene.DateTime()


class LikeableType(graphene.Interface):
    likes = graphene.Int()

    @classmethod
    def resolve_type(cls, instance, info):
        type_class_name = instance.__class__.get_type()
        return getattr(info.schema, type_class_name)


class CommentType(GettableMixin, ObjectType):
    class Meta:
        interfaces = (LikeableType, BaseDatedType)

    content = graphene.String(required=True)
    about = graphene.Field(LikeableType)

    @staticmethod
    def _get_node(uid):
        return CommentNode.nodes.get(uid=uid)

    @staticmethod
    def _get_error():
        return Exception(COMMENT_NOT_FOUND_ERROR)

    def resolve_about(parent, info):
        return parent.about.single()


class CommentableType(graphene.Interface):
    comments = graphene.Int()
    comments_list = graphene.List(CommentType)

    def resolve_comments_list(parent, info):
        return parent.commented.all()


class TweetType(GettableMixin, ObjectType):
    class Meta:
        interfaces = (LikeableType, CommentableType, BaseDatedType)

    content = graphene.String(required=True)
    retweets = graphene.Int()

    @staticmethod
    def _get_node(uid):
        return TweetNode.nodes.get(uid=uid)

    @staticmethod
    def _get_error():
        return Exception(TWEET_NOT_FOUND_ERROR)


class ReTweetType(GettableMixin, ObjectType):
    class Meta:
        interfaces = (LikeableType, CommentableType, BaseDatedType)

    tweet = graphene.Field(TweetType)

    @staticmethod
    def _get_node(uid):
        return ReTweetNode.nodes.get(uid=uid)

    @staticmethod
    def _get_error():
        return Exception(RETWEET_NOT_FOUND_ERROR)

    def resolve_tweet(parent, info):
        return parent.tweet.single()


class UserType(GettableMixin, ObjectType):
    class Meta:
        interfaces = (BaseDatedType,)

    uid = graphene.String(required=True, source="uid")
    email = graphene.String()
    username = graphene.String()
    followers_count = graphene.Int(source="followers_count")
    tweets = graphene.List(TweetType, first=graphene.Int(), skip=graphene.Int())
    retweets = graphene.List(ReTweetType, first=graphene.Int(), skip=graphene.Int())
    comments = graphene.List(CommentType, first=graphene.Int(), skip=graphene.Int())
    followers = graphene.List(lambda: UserType, first=graphene.Int(), skip=graphene.Int())
    follows = graphene.List(lambda: UserType, first=graphene.Int(), skip=graphene.Int())
    likes = graphene.List(LikeableType, first=graphene.Int(), skip=graphene.Int())

    @staticmethod
    def _get_node(uid):
        return UserNode.nodes.get(uid=uid)

    @staticmethod
    def _get_error():
        return Exception(USER_NOT_FOUND_ERROR)

    @classmethod
    def get_node_from_context(cls, info):
        user_uid = info.context.user.uid
        return cls._get_node(user_uid)

    def resolve_email(parent, info):
        return User.objects.get(uid=parent.uid).email

    def resolve_username(parent, info):
        return User.objects.get(uid=parent.uid).username

    def resolve_tweets(parent, info, first=None, skip=None):
        qs = parent.tweets.order_by("-created")
        return GettableMixin.filter_qs(qs, first, skip)

    def resolve_retweets(parent, info, first=None, skip=None):
        qs = parent.retweets.order_by("-created")
        return GettableMixin.filter_qs(qs, first, skip)

    def resolve_comments(parent, info, first=None, skip=None):
        qs = parent.comments.order_by("-created")
        return GettableMixin.filter_qs(qs, first, skip)

    def resolve_followers(parent, info, first=None, skip=None):
        followers_keys = [follower.uid for follower in parent.followers.order_by("-created")]
        followers_keys = GettableMixin.filter_qs(followers_keys, first, skip)
        return user_loader.load_many(followers_keys)

    def resolve_follows(parent, info, first=None, skip=None):
        follows_keys = [followed.uid for followed in parent.follows.order_by("-created")]
        follows_keys = GettableMixin.filter_qs(follows_keys, first, skip)
        return user_loader.load_many(follows_keys)

    def resolve_likes(parent, info, first=None, skip=None):
        qs = parent.likes.order_by("-created")
        return GettableMixin.filter_qs(qs, first, skip)
