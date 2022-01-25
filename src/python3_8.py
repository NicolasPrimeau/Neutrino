import json
import traceback
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import sys


def handle_event(event, _):
    request = json.loads(event.get("body") or "{}")

    stdout, stderr = exec_code(request.get("source_code", ""))

    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps({
            "stdout": stdout,
            "stderr": stderr
        })
    }


def exec_code(source_code):
    output = StringIO()
    stderr = StringIO()
    with redirect_stdout(output), redirect_stderr(stderr):
        try:
            exec(source_code, globals(), globals())
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
    return output.getvalue(), stderr.getvalue()
