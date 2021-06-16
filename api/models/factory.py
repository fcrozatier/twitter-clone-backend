from abc import ABC, abstractmethod

from api.models import models
from api.models.config import COMMENTABLES, LIKEABLES


class NodeFactory(ABC):
    @classmethod
    def node_name(cls, type):
        return type.replace("Type", "Node")

    @classmethod
    def short_name(cls, type):
        return type.replace("Type", "")

    @classmethod
    def get_or_none(cls, uid, type):
        if cls.is_actionable(type):
            node_name = cls.node_name(type)
            node_class = vars(models)[node_name]
            return node_class.nodes.get_or_none(uid=uid)
        else:
            return None

    @classmethod
    @abstractmethod
    def is_actionable(cls, type):
        pass


class LikeableFactory(NodeFactory):
    """
    Returns a Likeable node class given its type as a string.
    Usage:
      LikeableFactory.get_node(<some_uid>, "TweetType") -> TweetNode
    """

    @classmethod
    def is_actionable(cls, type):
        """
        Verifies if node is likeable
        """
        short_name = cls.short_name(type)
        return short_name in LIKEABLES


class CommentableFactory(NodeFactory):
    """
    Returns a Commentable node class given its type as a string.
    Usage:
      CommentableFactory.get_node(<some_uid>, "TweetType") -> TweetNode
    """

    @classmethod
    def is_actionable(cls, type):
        """
        Verifies if node is commentable
        """
        short_name = cls.short_name(type)
        return short_name in COMMENTABLES
