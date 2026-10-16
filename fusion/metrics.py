"""Performance metrics and error calculation (slide: Metrics and Error Calculation)."""
import math


def precision(tp, fp):
    return tp / (tp + fp) if (tp + fp) else 0.0


def recall(tp, fn):
    return tp / (tp + fn) if (tp + fn) else 0.0


def f1(tp, fp, fn):
    p, r = precision(tp, fp), recall(tp, fn)
    return 2 * p * r / (p + r) if (p + r) else 0.0


def mae(y_true, y_pred):
    return sum(abs(a - b) for a, b in zip(y_true, y_pred)) / len(y_true)


def rmse(y_true, y_pred):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(y_true, y_pred)) / len(y_true))


def percent_error(measured, true):
    return abs(measured - true) / abs(true) * 100.0


def iou(box_a, box_b):
    """Boxes are (x1, y1, x2, y2)."""
    ix1, iy1 = max(box_a[0], box_b[0]), max(box_a[1], box_b[1])
    ix2, iy2 = min(box_a[2], box_b[2]), min(box_a[3], box_b[3])
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    area = lambda b: (b[2] - b[0]) * (b[3] - b[1])
    union = area(box_a) + area(box_b) - inter
    return inter / union if union else 0.0
