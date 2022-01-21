import json

import websocket
import websocket._exceptions

from chalicelib import ws_handler, ws_sender

WS_URL = "wss://dds81j87ij.execute-api.us-east-2.amazonaws.com/api/"


def get_connection():
    ws = websocket.WebSocket()
    ws.settimeout(3)
    ws.connect(WS_URL)
    return ws


def test_send_message():
    conn = get_connection()
    conn.send(json.dumps({
        "type": ws_handler.WSEventType.TEST,
        "data": {
            "message": "test"
        }
    }))
    assert json.loads(conn.recv()) == ws_sender.TestWSReply("test")


def test_send_none_message():
    conn = get_connection()
    conn.send(json.dumps({
        "type": ws_handler.WSEventType.TEST,
        "data": {
            "message": None
        }
    }))
    assert json.loads(conn.recv()) == ws_sender.TestWSReply(None)
