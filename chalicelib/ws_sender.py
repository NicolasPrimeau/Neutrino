from enum import Enum


class WSReplyType(str, Enum):
    TEXT = "text"

    def __str__(self):
        return self.value


class WSReply(dict):
    def __init__(self, event_type: WSReplyType):
        super().__init__()
        self.type = event_type

    @property
    def type(self) -> WSReplyType:
        return WSReplyType(self["type"])

    @type.setter
    def type(self, event_type: WSReplyType):
        self["type"] = str(event_type)


class TestWSReply(WSReply):
    def __init__(self, message: str):
        super().__init__(WSReplyType.TEXT)
        self.message = message

    @property
    def message(self) -> str:
        return WSReplyType(self["message"])

    @message.setter
    def message(self, message: str):
        self["message"] = message


class WSSender:

    def __init__(self, connection_id: str):
        self.connection_id = connection_id

    def send_message(self, message: WSReply):
        pass
