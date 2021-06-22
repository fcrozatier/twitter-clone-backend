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

# Relations


class DateTimeRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


# Abstract classes and Interfaces


class BaseNode:
    uid = UniqueIdProperty()
    created = DateTimeProperty(default_now=True)

    @classmethod
    def get_type(cls):
        return cls.__name__.replace("Node", "Type")


class LikeableNode(BaseNode, StructuredNode):
    likes = IntegerProperty(default=0)


class CommentableNode(StructuredNode):
    comments = IntegerProperty(default=0)
    commented = RelationshipFrom("CommentNode", "ABOUT")


# Concrete classes


class CommentNode(LikeableNode):
    content = StringProperty(required=True)
    about = RelationshipTo(CommentableNode, "ABOUT")


class TweetNode(CommentableNode, LikeableNode):
    content = StringProperty(required=True)
    retweets = IntegerProperty(default=0)


class ReTweetNode(CommentableNode, LikeableNode):
    tweet = RelationshipTo(TweetNode, "ORIGINAL")


class UserNode(BaseNode, StructuredNode):
    tweets = RelationshipTo(TweetNode, "TWEETS", model=DateTimeRel)
    retweets = RelationshipTo(ReTweetNode, "RETWEETS", model=DateTimeRel)
    likes = RelationshipTo(LikeableNode, "LIKES", model=DateTimeRel)
    comments = RelationshipTo(CommentNode, "COMMENTS", model=DateTimeRel)
    follows = RelationshipTo("UserNode", "FOLLOWS", model=DateTimeRel)
    followers = RelationshipFrom("UserNode", "FOLLOWS", model=DateTimeRel)
    followers_count = IntegerProperty(default=0)
