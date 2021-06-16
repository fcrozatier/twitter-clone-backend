from neomodel import (
    DateTimeProperty,
    IntegerProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    StructuredRel,
    UniqueIdProperty,
)
from neomodel.relationship_manager import RelationshipFrom


class TweetRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class LikeRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class ReTweetRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class CommentRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class LikeableNode(StructuredNode):
    uid = UniqueIdProperty()
    likes = IntegerProperty(default=0)
    created = DateTimeProperty(default_now=True)


class TweetNode(LikeableNode):
    content = StringProperty(required=True)
    comments = IntegerProperty(default=0)
    retweets = IntegerProperty(default=0)


class ReTweetNode(LikeableNode):
    comments = IntegerProperty(default=0)
    tweet = RelationshipTo(TweetNode, "ORIGINAL")


class CommentNode(LikeableNode):
    content = StringProperty(required=True)
    tweet = RelationshipTo(TweetNode, "ABOUT")


class UserNode(StructuredNode):
    uid = StringProperty(required=True)
    tweets = RelationshipTo(TweetNode, "TWEETS", model=TweetRel)
    retweets = RelationshipTo(ReTweetNode, "RETWEETS", model=ReTweetRel)
    likes = RelationshipTo(LikeableNode, "LIKES", model=LikeRel)
    comments = RelationshipTo(CommentNode, "COMMENTS", model=CommentRel)
