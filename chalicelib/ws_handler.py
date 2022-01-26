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
    SAVE = "save"
    RUN_OUTPUT = "run_output"

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

    @property
    def language_id(self) -> int:
        return self.get("data", {}).get("language_id")

    @property
    def full_update(self) -> bool:
        return self.get("data", {}).get("full_update", False)


class SaveEvent(WSEvent):
    @property
    def source_code(self) -> str:
        return self.get("data", {}).get("source_code")

    @property
    def language_id(self) -> int:
        return self.get("data", {}).get("language_id")


class RunOutputEvent(WSEvent):
    @property
    def stdout(self) -> str:
        return self.get("data", {}).get("stdout")

    @property
    def stderr(self) -> str:
        return self.get("data", {}).get("stderr")


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
        elif event.type == WSEventType.SAVE:
            self.save(SaveEvent(event))
        elif event.type == WSEventType.RUN_OUTPUT:
            self.run_output(RunOutputEvent(event))
        elif event.type == WSEventType.TEST:
            self.test(TestEvent(event))
        else:
            _logger.warning(f"Unknown event type: {message}")

    def register(self, event: RegisterEvent):
        connection_ids = ws_store.insert_new_connection(event.session_id, self.connection_id)
        connection_ids.remove(self.connection_id)
        for connection_id in connection_ids:
            self.sender.send_message(connection_id, ws_sender.NewParticipant(event.session_id))
            self.sender.send_message(self.connection_id, ws_sender.NewParticipant(event.session_id))

        if self._send_source_update_request(event.session_id, list(connection_ids)):
            return

        source_code, language_id = ws_store.get_source_code(event.session_id)
        if source_code:
            self.sender.send_message(self.connection_id, ws_sender.SourceUpdateReply(
                event.session_id, source_code, language_id=language_id, full_update=True
            ))
        else:
            self.sender.send_message(self.connection_id, ws_sender.SyncReadyReply(event.session_id))

    def _send_source_update_request(self, session_id, connection_ids):
        random.shuffle(connection_ids)
        for connection_id in connection_ids:
            if self.sender.send_message(connection_id, ws_sender.SourceUpdateRequest(session_id)):
                return True
        return False

    def deregister(self, event: DeregisterEvent):
        for connection_id in ws_store.remove_connection(event.session_id, self.connection_id):
            self.sender.send_message(connection_id, ws_sender.ParticipantDrop(event.session_id))

    def broadcast(self, event: SourceBroadcastEvent):
        self.sender.broadcast(event.session_id, self.connection_id, ws_sender.SourceUpdateReply(
            event.session_id,
            event.source_code,
            language_id=event.language_id,
            full_update=event.full_update
        ))

    def save(self, event: SaveEvent):
        ws_store.save_source_code(event.session_id, event.source_code, event.language_id)

    def run_output(self, event: RunOutputEvent):
        self.sender.broadcast(event.session_id, self.connection_id, ws_sender.RunOutputUpdate(
            event.session_id,
            stdout=event.stdout,
            stderr=event.stderr
        ))

    def test(self, event: TestEvent):
        self.sender.send_message(self.connection_id, ws_sender.TestWSReply(event.session_id, event.message))

    def disconnect(self):
        pass
