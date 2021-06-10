from neomodel import (
    DateTimeProperty,
    IntegerProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    StructuredRel,
    UniqueIdProperty,
)


class Likeable:
    # todo
    pass


class TweetRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class LikeRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class ReTweetRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class CommentRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


class TweetNode(StructuredNode):
    uid = UniqueIdProperty()
    content = StringProperty(required=True)
    likes = IntegerProperty(default=0)
    comments = IntegerProperty(default=0)
    created = DateTimeProperty(default_now=True)


class CommentNode(StructuredNode):
    uid = UniqueIdProperty()
    content = StringProperty(required=True)
    created = DateTimeProperty(default_now=True)
    tweet = RelationshipTo(TweetNode, "ABOUT")


class UserNode(StructuredNode):
    uid = StringProperty(required=True)
    tweets = RelationshipTo(TweetNode, "TWEETS", model=TweetRel)
    likes = RelationshipTo(TweetNode, "LIKES", model=LikeRel)
    comments = RelationshipTo(CommentNode, "COMMENTS", model=CommentRel)
