import io
import contextlib
import flask
from queue import Queue

AUTH_CODE = Queue()
PORT = 45932
app = flask.Flask(__name__)


@app.route('/')
def auth_callback():
    global AUTH_CODE
    code = flask.request.args.get('code')
    error = flask.request.args.get('error')
    if code:
        AUTH_CODE.put(code)
    if error:
        AUTH_CODE.put(None)
    html = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body>
    <script>window.close();</script>
</body>
</html>
"""
    return html, 200


def run(**kwargs):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        app.run(**kwargs)


if __name__ == '__main__':
    run(port=PORT)
