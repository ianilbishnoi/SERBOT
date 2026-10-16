"""Formulas used on the 'Formulas Derived' slide."""
import math
import statistics


def ultrasonic_distance_m(echo_time_s: float, temp_c: float = 25.0) -> float:
    """d = v * t / 2, with v = 331.3 + 0.606 * T (m/s)."""
    v = 331.3 + 0.606 * temp_c
    return v * echo_time_s / 2.0


def tilt_from_accel(ax: float, ay: float, az: float):
    """roll = atan2(ay, az); pitch = atan2(-ax, sqrt(ay^2 + az^2)). Returns degrees."""
    roll = math.degrees(math.atan2(ay, az))
    pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
    return roll, pitch


class ComplementaryFilter:
    """theta(k) = alpha * (theta(k-1) + omega * dt) + (1 - alpha) * theta_acc."""

    def __init__(self, alpha: float = 0.98):
        self.alpha = alpha
        self.angle = None

    def update(self, gyro_rate_dps: float, acc_angle_deg: float, dt: float) -> float:
        if self.angle is None:
            self.angle = acc_angle_deg
        else:
            self.angle = self.alpha * (self.angle + gyro_rate_dps * dt) + (1 - self.alpha) * acc_angle_deg
        return self.angle


def encoder_distance_m(ticks: int, wheel_radius_m: float, ppr: int) -> float:
    """s = 2 * pi * r * N / PPR."""
    return 2 * math.pi * wheel_radius_m * ticks / ppr


class ChangeDetector:
    """Change-based monitoring: z = (x - mu_base) / sigma_base, alert if |z| > z_limit."""

    def __init__(self, z_limit: float = 3.0, min_sigma: float = 1e-6):
        self.z_limit = z_limit
        self.min_sigma = min_sigma
        self.mu = None
        self.sigma = None

    def set_baseline(self, samples):
        self.mu = statistics.fmean(samples)
        self.sigma = max(statistics.pstdev(samples), self.min_sigma)

    def z_score(self, x: float) -> float:
        if self.mu is None:
            raise RuntimeError("baseline not set")
        return (x - self.mu) / self.sigma

    def is_change(self, x: float) -> bool:
        return abs(self.z_score(x)) > self.z_limit


def hazard_score(scores: dict, weights: dict) -> float:
    """R = sum(w_i * s_i), weights normalised so sum(w_i) = 1. Each s_i in [0, 1]."""
    total = sum(weights.values())
    return sum(weights[k] / total * min(max(scores.get(k, 0.0), 0.0), 1.0) for k in weights)
