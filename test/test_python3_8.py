import requests

URL = "https://o5brsfw8jd.execute-api.us-east-2.amazonaws.com/prod/neutrino-python-3_8"


def test_execute_simple_line():
    response = requests.post(URL, json={"source_code": 'print("Neutrino!")'})
    assert response.json().get("stdout") == "Neutrino!\n"


def test_multi_line():
    response = requests.post(URL, json={"source_code": "print(0)\nprint(1)\n"})
    assert response.json().get("stdout") == "0\n1\n"


def test_multi_line_dependency():
    response = requests.post(URL, json={"source_code": "for i in range(0, 3):\n  print(i)\n"})
    assert response.json().get("stdout") == "0\n1\n2\n"


def test_stderr():
    response = requests.post(URL, json={"source_code": "not_python"})
    assert "NameError: name 'not_python' is not defined" in response.json().get("stderr")


def test_import():
    response = requests.post(URL, json={"source_code": "import random; print(random.random());"})
    assert 0 <= float(response.json().get("stdout").strip()) < 1
