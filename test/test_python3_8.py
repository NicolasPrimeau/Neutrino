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
    assert response.json().get("stderr") == (
        'Traceback (most recent call last):\n'
         '  File "/var/task/python3_8.py", line 27, in exec_code\n'
         '    exec(source_code)\n'
         '  File "<string>", line 1, in <module>\n'
         "NameError: name 'not_python' is not defined\n"
         '\n'
    )

