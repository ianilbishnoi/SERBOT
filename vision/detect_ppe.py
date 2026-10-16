"""Real-time PPE check. Usage: python vision/detect_ppe.py --weights best.pt --source 0"""
import argparse
from collections import Counter

import cv2
from ultralytics import YOLO


def ppe_violations(counts: Counter) -> list:
    """Each detected person should have a helmet and a vest (simple count-based rule)."""
    persons = counts.get("person", 0)
    out = []
    if counts.get("helmet", 0) < persons:
        out.append("NO_HELMET")
    if counts.get("vest", 0) < persons:
        out.append("NO_VEST")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="yolov8n.pt")
    ap.add_argument("--source", default="0")
    ap.add_argument("--conf", type=float, default=0.4)
    a = ap.parse_args()
    model = YOLO(a.weights)
    cap = cv2.VideoCapture(int(a.source) if a.source.isdigit() else a.source)
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        res = model(cv2.resize(frame, (640, 640)), conf=a.conf, verbose=False)[0]
        counts = Counter(model.names[int(c)] for c in res.boxes.cls)
        viol = ppe_violations(counts)
        img = res.plot()
        cv2.putText(img, "ALERT: " + ",".join(viol) if viol else "PPE OK", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255) if viol else (0, 200, 0), 2)
        cv2.imshow("PPE", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
