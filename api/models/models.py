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

    def has_retweeted(self, tweet):
        params = {"userUID": self.uid, "tweetUID": tweet.uid}
        results, columns = self.cypher(
            """
            match (u:UserNode)-[:RETWEETS]->(n:ReTweetNode)-[:ORIGINAL]->(t:TweetNode)
            where u.uid = $userUID and t.uid = $tweetUID
            return count(n)
            """,
            params=params,
        )
        return results[0][0] > 0

    @staticmethod
    def auto_inflate_to_likeables(results):
        likeables_set = set(["TweetNode", "ReTweetNode", "CommentNode"])
        likeable_list = []

        for item in results:
            node_class_name = likeables_set.intersection(item[0].labels).pop()
            node_class = globals()[node_class_name]

            likeable_list.append(node_class.inflate(item[0]))
        return likeable_list

    def content(self, skip=0, limit=100):
        params = {"uid": self.uid, "skip": skip, "limit": limit}

        results, columns = self.cypher(
            """
            match (u:UserNode)-[r]->(n:LikeableNode)
            where u.uid = $uid
            return n
            order by r.date desc
            skip $skip
            limit $limit
            """,
            params=params,
        )

        return UserNode.auto_inflate_to_likeables(results)

    def feed(self, skip=0, limit=100):
        params = {"uid": self.uid, "skip": skip, "limit": limit}

        results, columns = self.cypher(
            """
            match (u:UserNode)-[:FOLLOWS]->(f:UserNode)-[r]->(n:LikeableNode)
            where u.uid = $uid
            return n
            order by r.date desc
            skip $skip
            limit $limit
            """,
            params=params,
        )

        return UserNode.auto_inflate_to_likeables(results)
