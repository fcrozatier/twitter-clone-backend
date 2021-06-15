import graphene
from accounts.decorators import login_required, user_verified
from api.errors import (
    ALREADY_LIKED_ERROR,
    COMMENT_EMPTY_ERROR,
    NOT_LIKEABLE,
    TWEET_EMPTY_ERROR,
    TWEET_NOT_FOUND_ERROR,
)
from api.models import CommentNode, ReTweetNode, TweetNode, UserNode
from api.models.factory import LikeableFactory
from api.schema.types import CommentType, LikeableType, ReTweetType, TweetType
from graphene.types.objecttype import ObjectType


class CreateLike(graphene.Mutation):
    class Arguments:
        uid = graphene.String(required=True)
        type = graphene.String(required=True)

    likeable = graphene.Field(LikeableType)

    @login_required
    def mutate(parent, info, uid, type):
        likeable = LikeableFactory().get_or_none(uid, type)
        if not likeable:
            raise Exception(NOT_LIKEABLE)

        user_uid = info.context.user.uid
        user = UserNode.nodes.get(uid=user_uid)
        if user.likes.is_connected(likeable):
            raise Exception(ALREADY_LIKED_ERROR)

        user.likes.connect(likeable)
        likeable.likes += 1
        likeable.save()
        return CreateLike(likeable=likeable)


class CreateTweet(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)

    tweet = graphene.Field(TweetType)

    @login_required
    @user_verified
    def mutate(parent, info, content):
        user_uid = info.context.user.uid
        if content == "":
            raise Exception(TWEET_EMPTY_ERROR)
        tweet = TweetNode(content=content).save()
        user = UserNode.nodes.get(uid=user_uid)
        user.tweets.connect(tweet)
        return CreateTweet(tweet=tweet)


class CreateReTweet(graphene.Mutation):
    class Arguments:
        tweet_uid = graphene.String(required=True)

    retweet = graphene.Field(ReTweetType)

    @login_required
    def mutate(parent, info, tweet_uid):
        tweet_node = TweetNode.nodes.get_or_none(uid=tweet_uid)
        if not tweet_node:
            raise Exception(TWEET_NOT_FOUND_ERROR)

        tweet_node.retweets += 1
        tweet_node.save()

        retweet_node = ReTweetNode().save()
        retweet_node.tweet.connect(tweet_node)

        user_uid = info.context.user.uid
        user_node = UserNode.nodes.get(uid=user_uid)
        user_node.retweets.connect(retweet_node)

        return CreateReTweet(retweet=retweet_node)


class CreateComment(graphene.Mutation):
    class Arguments:
        tweet_uid = graphene.String(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(CommentType)

    @login_required
    @user_verified
    def mutate(parent, info, tweet_uid, content):
        if content == "":
            raise Exception(COMMENT_EMPTY_ERROR)

        tweet = TweetNode.nodes.get_or_none(uid=tweet_uid)
        if not tweet:
            raise Exception(TWEET_NOT_FOUND_ERROR)

        comment_node = CommentNode(content=content).save()

        user_uid = info.context.user.uid
        user_node = UserNode.nodes.get(uid=user_uid)
        user_node.comments.connect(comment_node)

        tweet.comments += 1
        tweet.save()

        comment_node.tweet.connect(tweet)
        return CreateComment(comment=comment_node)


class Mutation(ObjectType):
    create_tweet = CreateTweet.Field()
    create_retweet = CreateReTweet.Field()
    create_like = CreateLike.Field()
    create_comment = CreateComment.Field()
