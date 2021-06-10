import graphene
from accounts.decorators import login_required, user_verified
from graphene.types.objecttype import ObjectType

from api.errors import COMMENT_EMPTY_ERROR, TWEET_EMPTY_ERROR, TWEET_NOT_FOUND_ERROR
from api.models import CommentNode, TweetNode, UserNode


class TweetType(graphene.ObjectType):
    uid = graphene.String(required=True)
    content = graphene.String(required=True)
    likes = graphene.Int()
    comments = graphene.Int()
    created = graphene.DateTime()

    def resolve_uid(parent, info):
        return parent.uid

    def resolve_content(parent, info):
        return parent.content

    def resolve_likes(parent, info):
        return parent.likes

    def resolve_comments(parent, info):
        return parent.comments


class CommentType(ObjectType):
    uid = graphene.String(required=True)
    content = graphene.String(required=True)
    created = graphene.DateTime()
    tweet = graphene.Field(TweetType)

    def resolve_uid(parent, info):
        return parent.uid

    def resolve_content(parent, info):
        return parent.content

    def resolve_tweet(parent, info):
        return parent.tweet.single()


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


class CreateLike(graphene.Mutation):
    class Arguments:
        tweet_uid = graphene.String(required=True)

    tweet = graphene.Field(TweetType)

    @login_required
    def mutate(parent, info, tweet_uid):
        tweet = TweetNode.nodes.get_or_none(uid=tweet_uid)
        if not tweet:
            raise Exception(TWEET_NOT_FOUND_ERROR)

        tweet.likes += 1
        tweet.save()
        user_uid = info.context.user.uid
        user = UserNode.nodes.get(uid=user_uid)
        user.likes.connect(tweet)
        return CreateLike(tweet=tweet)


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


class Query(graphene.ObjectType):
    tweets = graphene.List(TweetType)

    def resolve_tweets(root, info, **kwargs):
        return TweetNode.nodes.all()


class Mutation(ObjectType):
    create_tweet = CreateTweet.Field()
    create_like = CreateLike.Field()
    create_comment = CreateComment.Field()
