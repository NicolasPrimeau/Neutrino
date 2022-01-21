import json
import logging
from enum import Enum

from chalicelib import ws_sender

_logger = logging.getLogger()


class WSEventType(str, Enum):
    REGISTER = "register"
    TEST = "test"

    def __str__(self):
        return self.value


class WSEvent(dict):
    @property
    def type(self) -> WSEventType:
        event_str = self.get("type")
        return WSEventType(event_str) if event_str else None

    @classmethod
    def from_message(cls, data: str) -> "WSEvent":
        return WSEvent(json.loads(data))


class TestEvent(WSEvent):
    @property
    def message(self) -> str:
        return self.get("data", {}).get("message")


class RegisterEvent(WSEvent):
    @property
    def session_id(self) -> str:
        return self.get("data", {}).get("session_id")


class WSHandler:
    def __init__(self, connection_id: str, sender):
        self.connection_id = connection_id
        self.sender = sender

    def connect(self):
        pass

    def message(self, message: str):
        event = WSEvent.from_message(message)
        if event.type == WSEventType.REGISTER:
            self.register(RegisterEvent(event))
        elif event.type == WSEventType.TEST:
            self.test(TestEvent(event))
        else:
            _logger.warning(f"Unknown event type: {message}")

    def register(self, event: RegisterEvent):
        # set session id for connection id in DDB
        pass

    def test(self, event: TestEvent):
        self.sender.send_message(self.connection_id, ws_sender.TestWSReply(event.message))

    def disconnect(self):
        # remove session id for connection id in DDB
        pass
