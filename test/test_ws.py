import json

import pytest
import websocket
import websocket._exceptions

from chalicelib import ws_handler, ws_sender, ws_store

WS_URL = "wss://dds81j87ij.execute-api.us-east-2.amazonaws.com/api/"


def get_connection():
    ws = websocket.WebSocket()
    ws.settimeout(2)
    ws.connect(WS_URL)
    return ws


def test_send_test():
    conn = get_connection()
    conn.send(json.dumps({
        "type": ws_handler.WSEventType.TEST,
        "sessionId": "1",
        "data": {
            "message": "test"
        }
    }))
    assert json.loads(conn.recv()) == ws_sender.TestWSReply("1", "test")


def test_send_none_test():
    conn = get_connection()
    conn.send(json.dumps({
        "type": ws_handler.WSEventType.TEST,
        "sessionId": "1",
        "data": {
            "message": None
        }
    }))
    assert json.loads(conn.recv()) == ws_sender.TestWSReply("1", None)


def test_send_register():
    ws_store.delete_item("1")
    conn = get_connection()
    conn.send(json.dumps({
        "type": ws_handler.WSEventType.REGISTER,
        "sessionId": "1",
        "data": {
            "message": None
        }
    }))
    assert json.loads(conn.recv()) == {"type": "sync_ready", "session_id": "1", "data": {}}


def test_setup():
    ws_store.delete_item("1")
    conn1 = get_connection()
    conn1.send(json.dumps({
        "type": ws_handler.WSEventType.REGISTER,
        "sessionId": "1",
        "data": {}
    }))
    assert json.loads(conn1.recv()) == {"type": "sync_ready", "session_id": "1", "data": {}}

    conn2 = get_connection()
    conn2.send(json.dumps({
        "type": ws_handler.WSEventType.REGISTER,
        "sessionId": "1",
        "data": {}
    }))
    assert json.loads(conn1.recv()) == {"type": "new_participant", "session_id": "1", "data": {}}
    assert json.loads(conn2.recv()) == {"type": "new_participant", "session_id": "1", "data": {}}

    assert json.loads(conn1.recv()) == {"type": "source_update_request", "session_id": "1", "data": {}}
    conn1.send(json.dumps({
        "type": ws_handler.WSEventType.SOURCE_BROADCAST,
        "sessionId": "1",
        "data": {
            "source_code": 'print("Hello world")',
            "language_id": 1,
            "full_update": True
        }
    }))

    assert json.loads(conn2.recv()) == {
        "type": "source_update",
        "session_id": "1",
        "data": {
            "source_code": 'print("Hello world")',
            "language_id": 1,
            "full_update": True
        }
    }
    with pytest.raises(websocket._exceptions.WebSocketTimeoutException):
        conn1.recv()
