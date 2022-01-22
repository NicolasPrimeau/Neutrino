import json
from enum import Enum
from typing import Dict

from chalice import WebsocketDisconnectedError

from chalicelib import ws_store


class WSReplyType(str, Enum):
    TEXT = "text"
    SOURCE_UPDATE = "source_update"
    SOURCE_UPDATE_REQUEST = "source_update_request"
    SYNC_READY = "sync_ready"

    def __str__(self):
        return self.value


class WSReply(dict):
    def __init__(self, event_type: WSReplyType, session_id: str):
        super().__init__()
        self.type = event_type
        self.session_id = session_id
        self.data = {}

    @property
    def type(self) -> WSReplyType:
        return WSReplyType(self["type"])

    @type.setter
    def type(self, event_type: WSReplyType):
        self["type"] = str(event_type)

    @property
    def session_id(self) -> str:
        return self["session_id"]

    @session_id.setter
    def session_id(self, session_id: str):
        self["session_id"] = session_id

    @property
    def data(self) -> Dict:
        return self["data"]

    @data.setter
    def data(self, data: Dict):
        self["data"] = data

    def encode(self) -> str:
        return json.dumps(self)


class TestWSReply(WSReply):
    def __init__(self, session_id: str, message: str):
        super().__init__(WSReplyType.TEXT, session_id)
        self.message = message

    @property
    def message(self) -> str:
        return self.data["message"]

    @message.setter
    def message(self, message: str):
        self.data["message"] = message


class SourceUpdateReply(WSReply):
    def __init__(self, session_id: str, source_code: str):
        super().__init__(WSReplyType.SOURCE_UPDATE, session_id)
        self.source_code = source_code

    @property
    def source_code(self) -> str:
        return self.data["source_code"]

    @source_code.setter
    def source_code(self, source_code: str):
        self.data["source_code"] = source_code


class SyncReadyReply(WSReply):
    def __init__(self, session_id):
        super().__init__(WSReplyType.SYNC_READY, session_id)


class SourceUpdateRequest(WSReply):
    def __init__(self, session_id):
        super().__init__(WSReplyType.SOURCE_UPDATE_REQUEST, session_id)


class WSSender:
    def __init__(self, app):
        self.app = app

    def send_message(self, connection_id: str, reply: WSReply):
        try:
            self.app.websocket_api.send(
                connection_id=connection_id,
                message=reply.encode(),
            )
        except WebsocketDisconnectedError:
            ws_store.remove_connection(reply.session_id, connection_id)
