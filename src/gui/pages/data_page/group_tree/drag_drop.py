import json

from PySide6.QtCore import QMimeData

from .model import NodeType, MIME_DATA_IDS


MIME_GROUP_NODE = "application/x-moltenmeta-group-node"


def encodeDragData(
    node_type: NodeType, node_id: int | None, data_ids: list[int]
) -> QMimeData:
    mime = QMimeData()
    group_info = {
        "node_type": node_type.name,
        "node_id": node_id,
    }
    mime.setData(MIME_GROUP_NODE, json.dumps(group_info).encode())
    mime.setData(MIME_DATA_IDS, json.dumps(data_ids).encode())
    return mime


def decodeDragData(mime: QMimeData) -> tuple[NodeType, int | None, list[int]]:
    group_data = mime.data(MIME_GROUP_NODE)
    if group_data:
        info = json.loads(group_data.data())
        node_type = NodeType[info["node_type"]]
        node_id = info.get("node_id")
    else:
        node_type = None
        node_id = None

    data_data = mime.data(MIME_DATA_IDS)
    if data_data:
        data_ids = json.loads(data_data.data())
    else:
        data_ids = []

    return node_type, node_id, data_ids
