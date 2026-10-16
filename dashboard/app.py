"""Live dashboard. Run: python dashboard/app.py --broker localhost  then open http://localhost:5000"""
import argparse
import json
import threading

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template

app = Flask(__name__)
state = {"level": "NO DATA"}
history = []


def start_mqtt(broker):
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.on_connect = lambda cl, u, f, rc, p=None: cl.subscribe("site/alerts")

    def on_msg(cl, u, m):
        global state
        state = json.loads(m.payload)
        history.append(state)
        del history[:-200]

    c.on_message = on_msg
    c.connect(broker, 1883)
    threading.Thread(target=c.loop_forever, daemon=True).start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    return jsonify({"now": state, "history": history[-50:]})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--broker", default="localhost")
    a = ap.parse_args()
    start_mqtt(a.broker)
    app.run(host="0.0.0.0", port=5000)
