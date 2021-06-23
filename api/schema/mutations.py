import graphene
from accounts.decorators import login_required, user_verified
from api.errors import (
    ALREADY_LIKED_ERROR,
    ALREADY_RETWEETED_ERROR,
    COMMENT_EMPTY_ERROR,
    NOT_COMMENTABLE,
    NOT_LIKEABLE,
    TWEET_EMPTY_ERROR,
    UNFOLLOW_ERROR,
    UNLIKED_ERROR,
    USER_ALREADY_FOLLOWED_ERROR,
)
from api.models import CommentNode, ReTweetNode, TweetNode, UserNode
from api.schema.types import (
    CommentableType,
    CommentType,
    LikeableType,
    ReTweetType,
    TweetType,
    UserType,
)
from graphene.types.objecttype import ObjectType


class CreateComment(graphene.Mutation):
    class Arguments:
        uid = graphene.String(required=True)
        type = graphene.String(required=True)
        content = graphene.String(required=True)

    Output = CommentType

    @login_required
    @user_verified
    def mutate(parent, info, uid, type, content):
        if content == "":
            raise Exception(COMMENT_EMPTY_ERROR)

        try:
            type_cls = getattr(info.schema, type)
        except:
            raise Exception(NOT_COMMENTABLE)

        if CommentableType in type_cls._meta.interfaces:
            commentable = type_cls.get_node(uid)
        else:
            raise Exception(NOT_COMMENTABLE)

        comment_node = CommentNode(content=content).save()

        user_uid = info.context.user.uid
        user_node = UserType.get_node(uid=user_uid)
        user_node.comments.connect(comment_node)

        commentable.comments += 1
        commentable.save()

        comment_node.about.connect(commentable)
        return comment_node


class CreateLike(graphene.Mutation):
    class Arguments:
        uid = graphene.String(required=True)
        type = graphene.String(required=True)

    Output = LikeableType

    @login_required
    def mutate(parent, info, uid, type):
        try:
            type_cls = getattr(info.schema, type)
        except:
            raise Exception(NOT_LIKEABLE)

        if LikeableType in type_cls._meta.interfaces:
            likeable = type_cls.get_node(uid)
        else:
            raise Exception(NOT_LIKEABLE)

        user_uid = info.context.user.uid
        user = UserType.get_node(uid=user_uid)
        if user.likes.is_connected(likeable):
            raise Exception(ALREADY_LIKED_ERROR)

        user.likes.connect(likeable)
        likeable.likes += 1
        likeable.save()

        return likeable


class DeleteLike(graphene.Mutation):
    class Arguments:
        uid = graphene.String(required=True)
        type = graphene.String(required=True)

    Output = LikeableType

    @login_required
    def mutate(parent, info, uid, type):
        try:
            type_cls = getattr(info.schema, type)
            if LikeableType in type_cls._meta.interfaces:
                likeable = type_cls.get_node(uid)
            else:
                raise Exception(UNLIKED_ERROR)
        except:
            raise Exception(UNLIKED_ERROR)

        user_uid = info.context.user.uid
        user = UserType.get_node(uid=user_uid)
        if not user.likes.is_connected(likeable):
            raise Exception(UNLIKED_ERROR)

        user.likes.disconnect(likeable)
        likeable.likes -= 1
        likeable.save()
        return likeable


class CreateTweet(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)

    Output = TweetType

    @login_required
    @user_verified
    def mutate(parent, info, content):
        user_uid = info.context.user.uid
        if content == "":
            raise Exception(TWEET_EMPTY_ERROR)

        tweet = TweetNode(content=content).save()
        user = UserType.get_node(uid=user_uid)
        user.tweets.connect(tweet)

        return tweet


class CreateReTweet(graphene.Mutation):
    class Arguments:
        uid = graphene.String(required=True)

    Output = ReTweetType

    @login_required
    def mutate(parent, info, uid):
        user = UserType.get_node_from_context(info)
        tweet_node = TweetType.get_node(uid=uid)

        if user.has_retweeted(tweet_node):
            raise Exception(ALREADY_RETWEETED_ERROR)

        tweet_node.retweets += 1
        tweet_node.save()

        retweet_node = ReTweetNode().save()
        retweet_node.tweet.connect(tweet_node)
        user.retweets.connect(retweet_node)

        return retweet_node


class FollowUser(graphene.Mutation):
    class Arguments:
        uid = graphene.String(required=True)

    Output = UserType

    @login_required
    def mutate(parent, info, uid):
        user = UserType.get_node(uid=uid)

        follower_uid = info.context.user.uid
        follower = UserNode.nodes.get(uid=follower_uid)
        if follower.follows.is_connected(user):
            raise Exception(USER_ALREADY_FOLLOWED_ERROR)

        follower.follows.connect(user)

        user.followers_count += 1
        user.save()

        return user


class UnFollowUser(graphene.Mutation):
    class Arguments:
        uid = graphene.String(required=True)

    Output = UserType

    @login_required
    def mutate(parent, info, uid):
        user = UserType.get_node(uid=uid)

        follower_uid = info.context.user.uid
        follower = UserType.get_node(uid=follower_uid)
        if not follower.follows.is_connected(user):
            raise Exception(UNFOLLOW_ERROR)

        follower.follows.disconnect(user)

        user.followers_count -= 1
        user.save()

        return user


class Mutation(ObjectType):
    tweet = CreateTweet.Field()
    retweet = CreateReTweet.Field()
    like = CreateLike.Field()
    unlike = DeleteLike.Field()
    comment = CreateComment.Field()
    follow = FollowUser.Field()
    unfollow = UnFollowUser.Field()
