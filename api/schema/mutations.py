import graphene
from accounts.decorators import login_required, user_verified
from api.errors import (
    ALREADY_LIKED_ERROR,
    ALREADY_RETWEETED_ERROR,
    COMMENT_EMPTY_ERROR,
    NOT_COMMENTABLE,
    NOT_LIKEABLE,
    TWEET_EMPTY_ERROR,
    TWEET_TOO_LONG_ERROR,
    UNFOLLOW_ERROR,
    UNLIKED_ERROR,
    USER_ALREADY_FOLLOWED_ERROR,
)
from api.models.models import CommentNode, ReTweetNode, TweetNode
from api.schema.types import (
    CommentableType,
    CommentType,
    HashtagType,
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

        user_node = UserType.get_node_from_context(info)
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

        user = UserType.get_node_from_context(info)
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

        user = UserType.get_node_from_context(info)
        if not user.likes.is_connected(likeable):
            raise Exception(UNLIKED_ERROR)

        user.likes.disconnect(likeable)
        likeable.likes -= 1
        likeable.save()
        return likeable


class CreateTweet(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)
        hashtags = graphene.List(graphene.NonNull(graphene.String))

    Output = TweetType

    @login_required
    @user_verified
    def mutate(parent, info, content, hashtags=None):
        if content == "":
            raise Exception(TWEET_EMPTY_ERROR)
        if len(content) >= 150:
            raise Exception(TWEET_TOO_LONG_ERROR)

        tweet = TweetNode(content=content).save()
        user = UserType.get_node_from_context(info)
        user.tweets.connect(tweet)

        if hashtags and hashtags != []:
            for tag in hashtags:
                hashtag_node = HashtagType.get_or_create(tag.strip())
                hashtag_node.tags += 1
                hashtag_node.save()
                tweet.hashtags.connect(hashtag_node)

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

        follower = UserType.get_node_from_context(info)
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

        follower = UserType.get_node_from_context(info)
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
