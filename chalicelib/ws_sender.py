import json
from enum import Enum
from typing import Dict

from chalice import WebsocketDisconnectedError


class WSReplyType(str, Enum):
    TEXT = "text"
    SOURCE_UPDATE = "SOURCE_UPDATE"

    def __str__(self):
        return self.value


class WSReply(dict):
    def __init__(self, event_type: WSReplyType):
        super().__init__()
        self.type = event_type
        self.data = {}

    @property
    def type(self) -> WSReplyType:
        return WSReplyType(self["type"])

    @type.setter
    def type(self, event_type: WSReplyType):
        self["type"] = str(event_type)

    @property
    def data(self) -> Dict:
        return self["data"]

    @data.setter
    def data(self, data: Dict):
        self["data"] = data

    def encode(self) -> str:
        return json.dumps(self)


class TestWSReply(WSReply):
    def __init__(self, message: str):
        super().__init__(WSReplyType.TEXT)
        self.message = message

    @property
    def message(self) -> str:
        return self.data["message"]

    @message.setter
    def message(self, message: str):
        self.data["message"] = message


class SourceUpdateReply(WSReply):
    def __init__(self, text: str):
        super().__init__(WSReplyType.SOURCE_UPDATE)
        self.text = text

    @property
    def text(self) -> str:
        return self.data["text"]

    @text.setter
    def text(self, text: str):
        self.data["text"] = text


class WSSender:

    def __init__(self, app):
        self.app = app

    def send_message(self, connection_id: str, message: WSReply):
        try:
            self.app.websocket_api.send(
                connection_id=connection_id,
                message=message.encode(),
            )
        except WebsocketDisconnectedError as e:
            pass
