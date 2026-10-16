"""Train a light YOLO model for PPE detection (papers [3], [4])."""
from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO("yolov8n.pt")            # nano model: small enough for Raspberry Pi
    model.train(data="vision/data.yaml", epochs=50, imgsz=640, batch=16, augment=True)
