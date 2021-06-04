from neomodel import (
    DateTimeProperty,
    IntegerProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    StructuredRel,
    UniqueIdProperty,
)


class TweetRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class ReTweetRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class Comment(StructuredNode):
    uid = UniqueIdProperty()
    content = StringProperty(required=True)
    created = DateTimeProperty(default_now=True)


class Tweet(StructuredNode):
    uid = UniqueIdProperty()
    content = StringProperty(required=True)
    likes = IntegerProperty(default=0)
    created = DateTimeProperty(default_now=True)
    comments = RelationshipTo(Comment, "COMMENTS")


class UserNode(StructuredNode):
    uid = StringProperty(required=True)
    tweets = RelationshipTo(Tweet, "TWEETS", model=TweetRel)
    likes = RelationshipTo(Tweet, "LIKES")
    comments = RelationshipTo(Comment, "COMMENTS")
