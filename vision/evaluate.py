"""Report precision, recall and mAP for the report/slides."""
import sys
from ultralytics import YOLO

weights = sys.argv[1] if len(sys.argv) > 1 else "runs/detect/train/weights/best.pt"
m = YOLO(weights).val(data="vision/data.yaml", imgsz=640)
print(f"Precision {m.box.mp:.3f}  Recall {m.box.mr:.3f}  mAP@0.5 {m.box.map50:.3f}  mAP@0.5:0.95 {m.box.map:.3f}")
