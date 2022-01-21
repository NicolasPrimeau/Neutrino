import json

from websocket import create_connection

from chalicelib import ws_handler

WS_URL = "wss://dds81j87ij.execute-api.us-east-2.amazonaws.com/api/"


def get_connection():
    return create_connection(WS_URL)


def test_send_message():
    ws = get_connection()
    ws.send(json.dumps({
        "type": ws_handler.WSEventType.TEST,
        "body": {
            "message": "test"
        }
    }))
    result = ws.recv()
    print(result)
