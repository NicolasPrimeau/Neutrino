import json
import logging
import random
from enum import Enum

from chalicelib import ws_sender, ws_store

_logger = logging.getLogger()


class WSEventType(str, Enum):
    REGISTER = "register"
    DEREGISTER = "deregister"
    SOURCE_BROADCAST = "source_broadcast"
    TEST = "test"

    def __str__(self):
        return self.value


class WSEvent(dict):
    @property
    def type(self) -> WSEventType:
        event_str = self.get("type")
        return WSEventType(event_str) if event_str else None

    @property
    def session_id(self) -> str:
        return self["sessionId"]

    @classmethod
    def from_message(cls, data: str) -> "WSEvent":
        return WSEvent(json.loads(data))


class TestEvent(WSEvent):
    @property
    def message(self) -> str:
        return self.get("data", {}).get("message")


class RegisterEvent(WSEvent):
    pass


class DeregisterEvent(WSEvent):
    pass


class SourceBroadcastEvent(WSEvent):
    @property
    def source_code(self) -> str:
        return self.get("data", {}).get("source_code")


class WSHandler:
    def __init__(self, connection_id: str, sender: ws_sender.WSSender):
        self.connection_id = connection_id
        self.sender = sender

    def connect(self):
        pass

    def message(self, message: str):
        event = WSEvent.from_message(message)
        if event.type == WSEventType.REGISTER:
            self.register(RegisterEvent(event))
        elif event.type == WSEventType.DEREGISTER:
            self.deregister(DeregisterEvent(event))
        elif event.type == WSEventType.SOURCE_BROADCAST:
            self.broadcast(SourceBroadcastEvent(event))
        elif event.type == WSEventType.TEST:
            self.test(TestEvent(event))
        else:
            _logger.warning(f"Unknown event type: {message}")

    def register(self, event: RegisterEvent):
        connection_ids = ws_store.insert_new_connection(event.session_id, self.connection_id)
        connection_ids.remove(self.connection_id)
        if not connection_ids:
            return self.sender.send_message(self.connection_id, ws_sender.SyncReadyReply(event.session_id))

        recipient_id = random.choice(list(connection_ids))
        self.sender.send_message(recipient_id, ws_sender.SourceUpdateRequest(event.session_id))

    def deregister(self, event: DeregisterEvent):
        ws_store.remove_connection(event.session_id, self.connection_id)

    def broadcast(self, event: SourceBroadcastEvent):
        connection_ids = ws_store.get_connection_ids_for_session(event.session_id)
        if self.connection_id not in connection_ids:
            return

        connection_ids.remove(self.connection_id)
        for connection_id in connection_ids:
            self.sender.send_message(
                connection_id,
                ws_sender.SourceUpdateReply(event.session_id, event.source_code)
            )

    def test(self, event: TestEvent):
        self.sender.send_message(self.connection_id, ws_sender.TestWSReply(event.session_id, event.message))

    def disconnect(self):
        pass
