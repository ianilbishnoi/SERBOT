"""Subscribes to ESP32 sensor data (MQTT), applies filters and fusion, publishes alerts.

Run:  python fusion/hazard_node.py --broker localhost
Topics: site/sensors (in), site/alerts (out)
"""
import argparse
import csv
import json
import time

import paho.mqtt.client as mqtt

from filters import ComplementaryFilter, ChangeDetector, tilt_from_accel, ultrasonic_distance_m, hazard_score

WEIGHTS = {"tilt": 0.35, "gas": 0.30, "obstacle": 0.20, "env": 0.15}
GAS_LIMIT = 2000        # raw ADC counts treated as dangerous (calibrate for your MQ sensor)
SAFE_DIST_M = 0.50      # obstacle score rises as distance drops below this
TEMP_LIMIT_C = 45.0
WARN, DANGER = 0.4, 0.7
BASELINE_N = 50         # first N samples define the "normal" tilt


class HazardNode:
    def __init__(self, log_path="data/log.csv"):
        self.roll_f, self.pitch_f = ComplementaryFilter(), ComplementaryFilter()
        self.change = ChangeDetector(z_limit=3.0, min_sigma=0.05)  # 0.05 deg floor: avoids huge z when baseline is very steady
        self.baseline, self.last_t = [], None
        self.log = open(log_path, "a", newline="")
        self.writer = csv.writer(self.log)

    def process(self, d: dict) -> dict:
        now = d.get("t", time.time() * 1000) / 1000.0
        dt = (now - self.last_t) if self.last_t else 0.1
        self.last_t = now
        r_acc, p_acc = tilt_from_accel(d["ax"], d["ay"], d["az"])
        roll = self.roll_f.update(d["gx"], r_acc, dt)
        pitch = self.pitch_f.update(d["gy"], p_acc, dt)
        tilt = max(abs(roll), abs(pitch))

        if self.change.mu is None:
            self.baseline.append(tilt)
            if len(self.baseline) >= BASELINE_N:
                self.change.set_baseline(self.baseline)
            return {"level": "CALIBRATING", "tilt": tilt}

        z = self.change.z_score(tilt)
        dist_m = ultrasonic_distance_m(d["echo_us"] * 1e-6, d.get("temp", 25.0)) if d.get("echo_us") else 9.9
        scores = {
            "tilt": min(abs(z) / 6.0, 1.0),
            "gas": min(d.get("gas", 0) / GAS_LIMIT, 1.0),
            "obstacle": max(0.0, 1.0 - dist_m / SAFE_DIST_M),
            "env": min(max(d.get("temp", 25.0) - 30.0, 0) / (TEMP_LIMIT_C - 30.0), 1.0),
        }
        r = hazard_score(scores, WEIGHTS)
        level = "DANGER" if r >= DANGER else "WARNING" if r >= WARN else "SAFE"
        out = {"level": level, "risk": round(r, 3), "tilt_deg": round(tilt, 2), "z": round(z, 2),
               "dist_m": round(dist_m, 2), "gas": d.get("gas"), "temp": d.get("temp"), "hum": d.get("hum")}
        self.writer.writerow([now, tilt, z, dist_m, d.get("gas"), d.get("temp"), r, level])
        self.log.flush()
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--broker", default="localhost")
    ap.add_argument("--port", type=int, default=1883)
    a = ap.parse_args()
    node = HazardNode()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(c, u, f, rc, p=None):
        c.subscribe("site/sensors")

    def on_message(c, u, msg):
        try:
            c.publish("site/alerts", json.dumps(node.process(json.loads(msg.payload))))
        except (KeyError, ValueError) as e:
            print("bad packet:", e)

    client.on_connect, client.on_message = on_connect, on_message
    client.connect(a.broker, a.port)
    client.loop_forever()


if __name__ == "__main__":
    main()
