from neomodel import (
    DateTimeProperty,
    IntegerProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    StructuredRel,
    UniqueIdProperty,
    db,
)
from neomodel.relationship_manager import RelationshipFrom

# Relations


class DateTimeRel(StructuredRel):
    date = DateTimeProperty(default_now=True)


# Abstract classes and Interfaces


class BaseNode(StructuredNode):
    __abstract_node__ = True

    uid = UniqueIdProperty()
    created = DateTimeProperty(default_now=True)

    @classmethod
    def get_type(cls):
        return cls.__name__.replace("Node", "Type")


class LikeableNode(BaseNode):
    likes = IntegerProperty(default=0)


class CommentableNode(StructuredNode):
    comments = IntegerProperty(default=0)
    commented = RelationshipFrom("CommentNode", "ABOUT")


# Concrete classes


class HashtagNode(BaseNode):
    tag = StringProperty(required=True, unique_index=True)
    tags = IntegerProperty(default=0)
    tagged_by = RelationshipFrom("TweetNode", "HASHTAG")


class CommentNode(LikeableNode):
    content = StringProperty(required=True)
    about = RelationshipTo(CommentableNode, "ABOUT")
    author = RelationshipFrom("UserNode", "COMMENTS", model=DateTimeRel)


class TweetNode(CommentableNode, LikeableNode):
    content = StringProperty(required=True, max_length=150)
    retweets = IntegerProperty(default=0)
    hashtags = RelationshipTo(HashtagNode, "HASHTAG", model=DateTimeRel)
    author = RelationshipFrom("UserNode", "TWEETS", model=DateTimeRel)

class ReTweetNode(CommentableNode, LikeableNode):
    tweet = RelationshipTo(TweetNode, "ORIGINAL")
    author = RelationshipFrom("UserNode", "RETWEETS", model=DateTimeRel)


class UserNode(BaseNode):
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

    def content(self, skip=0, limit=100):
        params = {"uid": self.uid, "skip": skip, "limit": limit}

        results, meta = db.cypher_query(
            """
            match (u:UserNode)-[r:TWEETS|RETWEETS]->(n:LikeableNode)
            where u.uid = $uid
            return n
            order by r.date desc
            skip $skip
            limit $limit
            """,
            params=params,
            resolve_objects=True,
        )

        return [item[0] for item in results]

    def feed(self, skip=0, limit=100):
        params = {"uid": self.uid, "skip": skip, "limit": limit}

        results, meta = db.cypher_query(
            """
            match (u:UserNode)-[:FOLLOWS]->(f:UserNode)-[r:TWEETS|RETWEETS]->(n:LikeableNode)
            where u.uid = $uid
            return n
            order by r.date desc
            skip $skip
            limit $limit
            """,
            params=params,
            resolve_objects=True,
        )

        return [item[0] for item in results]
