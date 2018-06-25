import os
import jsonpickle
from threading import Thread
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

VERIFICATION_TOKEN = os.environ.get('V_TOKEN')
APP_TOKEN = os.environ.get('A_TOKEN')
CHANNEL = os.environ.get('A_IN_CHANNEL')


class SlackMessage(object):
    def __init__(self, user: str, text: str):
        self.channel = "#translations"
        self.user = user
        self.text = text


@app.route('/slack', methods=['POST'])
def pick_char():
    data = request.get_json()
    token = data.get('token', None)
    if token != VERIFICATION_TOKEN:
        Exception(f"IllegalRequest, got t='{token}'")

    challenge = data.get('challenge', None)
    if challenge is not None:
        return challenge

    event = data.get('event', {})
    type = event.get('type', None)
    channel = event.get('channel')

    if type == 'message' and channel == CHANNEL:
        text = event.get('text', '')
        user = event.get('user', None)

        if text and user is not None:
            msg = SlackMessage(user, text)
            t = Thread(target=mangle_post, args=(msg,))
            t.start()

    return "Ok"


def mangle_post(msg):
    msg.text = make_translation(msg.text)
    data = jsonpickle.encode(msg, unpicklable=False)
    print(f"sending {data}")
    headers = {'Authorization': f"Bearer {APP_TOKEN}"}
    res = requests.post('https://slack.com/api/chat.postMessage', json=data, headers=headers)
    print(f"got res={res}, json={res.json()}")


def make_translation(text):
    return "replaced the text!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
