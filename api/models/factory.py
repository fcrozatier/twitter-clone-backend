from api.errors import NOT_LIKEABLE
from api.models import models
from api.models.config import LIKEABLES


class LikeableFactory:
    """
    Returns a Likeable node class given its type as a string.
    Usage:
      LikeableFactory.get_node(<some_uid>, "TweetType") -> TweetNode
    """

    @classmethod
    def get_or_none(cls, uid, type):
        if cls.is_likeable(type):
            node_name = cls.node_name(type)
            node_class = vars(models)[node_name]
            return node_class.nodes.get_or_none(uid=uid)
        else:
            return None

    @classmethod
    def node_name(cls, type):
        return type.replace("Type", "Node")

    @classmethod
    def short_name(cls, type):
        return type.replace("Type", "")

    @classmethod
    def is_likeable(cls, type):
        short_name = cls.short_name(type)
        return short_name in LIKEABLES
