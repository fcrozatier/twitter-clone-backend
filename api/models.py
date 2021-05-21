from neomodel import (
    DateTimeProperty,
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


class Post(StructuredNode):
    uid = UniqueIdProperty()
    content = StringProperty(required=True)
    created = DateTimeProperty(default_now=True)


class Comment(StructuredNode):
    uid = UniqueIdProperty()
    content = StringProperty(required=True)
    created = DateTimeProperty(default_now=True)
    comments = RelationshipTo(Post, "COMMENTS")


class User(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    tweets = RelationshipTo(Post, "TWEETS", model=TweetRel)
    retweets = RelationshipTo(Post, "RETWEETS", model=ReTweetRel)
    likes = RelationshipTo(Post, "LIKES")
    reactions = RelationshipTo(Comment, "REACTION")
