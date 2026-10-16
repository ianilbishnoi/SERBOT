import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from filters import *      # noqa: E402
from metrics import *      # noqa: E402


def test_ultrasonic_distance():
    # 5.8 ms round trip at 20 C is about 1.0 m
    assert abs(ultrasonic_distance_m(0.0058, 20) - 0.995) < 0.01


def test_tilt_flat_and_tilted():
    assert tilt_from_accel(0, 0, 1) == (0.0, 0.0)
    roll, _ = tilt_from_accel(0, 1, 1)
    assert abs(roll - 45) < 1e-6


def test_complementary_filter_converges():
    f = ComplementaryFilter(0.98)
    for _ in range(500):
        a = f.update(0.0, 10.0, 0.01)
    assert abs(a - 10) < 0.1


def test_change_detector():
    c = ChangeDetector()
    c.set_baseline([1.0, 1.1, 0.9, 1.0, 1.05, 0.95])
    assert not c.is_change(1.02)
    assert c.is_change(3.0)


def test_hazard_score_bounds():
    assert hazard_score({"a": 1, "b": 1}, {"a": 1, "b": 1}) == 1.0
    assert hazard_score({}, {"a": 1}) == 0.0


def test_encoder_distance():
    assert abs(encoder_distance_m(20, 0.03, 20) - 2 * math.pi * 0.03) < 1e-9


def test_metrics():
    assert precision(8, 2) == 0.8 and recall(8, 2) == 0.8
    assert abs(f1(8, 2, 2) - 0.8) < 1e-9
    assert mae([1, 2], [2, 4]) == 1.5
    assert abs(rmse([0, 0], [3, 4]) - math.sqrt(12.5)) < 1e-9
    assert percent_error(1.05, 1.0) == 5.000000000000004 or abs(percent_error(1.05, 1.0) - 5) < 1e-9
    assert iou((0, 0, 2, 2), (1, 1, 3, 3)) == 1 / 7
