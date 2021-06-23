import inspect
import sys

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

    def content(self, skip=0, limit=100):
        params = {"uid": self.uid, "skip": skip, "limit": limit}

        results, columns = self.cypher(
            """match (u:UserNode)-[r]->(n:LikeableNode)
            where u.uid = $uid
            return n
            order by r.date desc
            skip $skip
            limit $limit
            """,
            params=params,
        )

        likeableset = set(["TweetNode", "ReTweetNode", "CommentNode"])
        likeable_list = []

        for item in results:
            node_class_name = likeableset.intersection(item[0].labels).pop()

            for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass):
                if name == node_class_name:
                    node_class = obj

            likeable_list.append(node_class.inflate(item[0]))

        return likeable_list
