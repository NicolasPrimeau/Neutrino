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
    RUN_OUTPUT_UPDATE = "run_output_update"
    NEW_PARTICIPANT = "new_participant"
    PARTICIPANT_DROP = "participant_drop"

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
    def __init__(self, session_id: str, source_code: str, language_id: int, full_update=False):
        super().__init__(WSReplyType.SOURCE_UPDATE, session_id)
        self.source_code = source_code
        self.language_id = language_id
        self.full_update = full_update

    @property
    def source_code(self) -> str:
        return self.data["source_code"]

    @source_code.setter
    def source_code(self, source_code: str):
        self.data["source_code"] = source_code

    @property
    def language_id(self) -> int:
        return self.data["language_id"]

    @language_id.setter
    def language_id(self, language_id: int):
        self.data["language_id"] = language_id

    @property
    def full_update(self) -> bool:
        return self.data["full_update"]

    @full_update.setter
    def full_update(self, full_update: bool):
        self.data["full_update"] = full_update


class SyncReadyReply(WSReply):
    def __init__(self, session_id):
        super().__init__(WSReplyType.SYNC_READY, session_id)


class NewParticipant(WSReply):
    def __init__(self, session_id):
        super().__init__(WSReplyType.NEW_PARTICIPANT, session_id)


class ParticipantDrop(WSReply):
    def __init__(self, session_id):
        super().__init__(WSReplyType.PARTICIPANT_DROP, session_id)


class SourceUpdateRequest(WSReply):
    def __init__(self, session_id):
        super().__init__(WSReplyType.SOURCE_UPDATE_REQUEST, session_id)


class RunOutputUpdate(WSReply):
    def __init__(self, session_id: str, stdout: str, stderr: str):
        super().__init__(WSReplyType.RUN_OUTPUT_UPDATE, session_id)
        self.stdout = stdout
        self.stderr = stderr

    @property
    def stdout(self) -> str:
        return self.data["stdout"]

    @stdout.setter
    def stdout(self, stdout: str):
        self.data["stdout"] = stdout

    @property
    def stderr(self) -> str:
        return self.data["stderr"]

    @stderr.setter
    def stderr(self, stderr: str):
        self.data["stderr"] = stderr


class WSSender:
    def __init__(self, app):
        self.app = app

    def broadcast(self, session_id: str, receiver_id: str, reply: WSReply) -> bool:
        connection_ids = ws_store.get_connection_ids_for_session(session_id)
        if receiver_id not in connection_ids:
            return False

        connection_ids.remove(receiver_id)
        sent = 0
        for connection_id in connection_ids:
            result = self.send_message(connection_id, reply)
            sent += 1 if result else 0
        return sent > 0

    def send_message(self, connection_id: str, reply: WSReply) -> bool:
        try:
            self.app.websocket_api.send(
                connection_id=connection_id,
                message=reply.encode(),
            )
            return True
        except WebsocketDisconnectedError:
            connection_ids = ws_store.remove_connection(reply.session_id, connection_id)
            for connection_id in connection_ids:
                self.send_message(connection_id, ParticipantDrop(reply.session_id))
            return False
