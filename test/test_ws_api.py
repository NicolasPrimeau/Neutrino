import requests

RES_API_URL = "https://ckc08f6h01.execute-api.us-east-2.amazonaws.com/api/"


def test_new_session():
    data = requests.post(RES_API_URL + "session/new")
    assert len(data.json()["name"].split("-")) == 5
