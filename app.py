from threading import Thread
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

VERIFICATION_TOKEN = ""  # put it here
APP_TOKEN = ""  # put it here


class SlackMessage(object):
    def __init__(self, ts: str, channel: str, text: str):
        self.token = APP_TOKEN
        self.ts = ts
        self.channel = channel
        self.text = text


@app.route('/slack', methods=['POST'])
def pick_char():
    print(f"got request={request}")
    data = request.get_json()
    token = data.get('token', None)
    if token != VERIFICATION_TOKEN:
        pass
        # raise Exception(f"IllegalRequest, got t='{token}'")

    event = data.get('event', {})
    type = event.get('type', None)
    if type == 'message':
        channel = event.get('channel', None)
        text = event.get('text', '')
        ts = event.get('ts', None)
        if channel is not None and text and ts is not None:
            msg = SlackMessage(ts, channel, text)
            t = Thread(target=mangle_post, args=(msg,))
            t.start()

    return "Ok"


def mangle_post(msg):
    new_msg = msg.copy()
    new_msg.text = "replaced the text!"
    data = jsonpickle.encode(new_msg, unpicklable=False)
    requests.post('https://slack.com/api/chat.update', json=data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
