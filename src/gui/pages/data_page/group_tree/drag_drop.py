import json

from PySide6.QtCore import QMimeData

from .model import NodeType, MIME_DATA_IDS


def decodeDragData(mime: QMimeData) -> tuple[NodeType, int | None, list[int]]:
    data_data = mime.data(MIME_DATA_IDS)
    if data_data:
        try:
            data_ids = json.loads(data_data.data())
        except (json.JSONDecodeError, TypeError):
            data_ids = []
    else:
        data_ids = []

    return None, None, data_ids
