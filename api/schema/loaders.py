from api.models import UserNode
from promise import Promise
from promise.dataloader import DataLoader


class UserLoader(DataLoader):
    def batch_load_fn(self, keys):
        return Promise.resolve([UserNode.nodes.get(uid=uid) for uid in keys])
