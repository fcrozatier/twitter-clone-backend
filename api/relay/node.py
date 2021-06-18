from api.relay import Node
from api.relay.id_types import UUIDGlobalIDType


class CustomNode(Node):
    class Meta:
        global_id_type = UUIDGlobalIDType
