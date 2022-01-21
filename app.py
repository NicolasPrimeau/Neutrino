from boto3.session import Session

from chalice import Chalice

from chalicelib import ws_handler

app = Chalice(app_name="neutrino-ws")
app.websocket_api.session = Session()
app.experimental_feature_flags.update([
    'WEBSOCKETS'
])


@app.on_ws_connect()
def connect(event):
    ws_handler.WSHandler(event.connection_id).connect()


@app.on_ws_message()
def message(event):
    ws_handler.WSHandler(event.connection_id).message(event.body)


@app.on_ws_disconnect()
def disconnect(event):
    ws_handler.WSHandler(event.connection_id).disconnect()
