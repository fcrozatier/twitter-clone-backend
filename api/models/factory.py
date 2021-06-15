from api.errors import NOT_LIKEABLE
from api.models import models
from api.models.config import LIKEABLES


class LikeableFactory:
    """
    Returns a Likeable node class given its type as a string.
    Usage:
      LikeableFactory().get_node(<some_uid>, "TweetType") -> TweetNode
    """

    def get_or_none(self, uid, type):
        if self.is_likeable(type):
            node_name = self.node_name(type)
            node_class = vars(models)[node_name]
            return node_class.nodes.get_or_none(uid=uid)
        else:
            return None

    def node_name(self, type):
        return type.replace("Type", "Node")

    def short_name(self, type):
        return type.replace("Type", "")

    def is_likeable(self, type):
        short_name = self.short_name(type)
        return short_name in LIKEABLES
