"""센서 스켈레톤 (planar, spherical).
각 센서는 accumulate(hit) 인터페이스 제공.
"""
from dataclasses import dataclass
from typing import Tuple
import numpy as np

@dataclass
class PlanarSensor:
    size_mm: Tuple[float, float]
    res: Tuple[int, int]
    distance_mm: float
    def __post_init__(self):
        self.buffer = np.zeros(self.res, dtype=np.float32)
    def accumulate(self, x, y, energy: float):
        i = int((x / self.size_mm[0] + 0.5) * self.res[0])
        j = int((y / self.size_mm[1] + 0.5) * self.res[1])
        if 0 <= i < self.res[0] and 0 <= j < self.res[1]:
            self.buffer[i, j] += energy

@dataclass
class SphericalSensor:
    theta_step_deg: float
    phi_step_deg: float
    distance_mm: float
    def __post_init__(self):
        th_bins = int(180 / self.theta_step_deg) + 1
        ph_bins = int(360 / self.phi_step_deg) + 1
        self.buffer = np.zeros((th_bins, ph_bins), dtype=np.float32)
    def accumulate(self, theta_deg: float, phi_deg: float, energy: float):
        i = int(theta_deg / self.theta_step_deg)
        j = int(phi_deg / self.phi_step_deg)
        if 0 <= i < self.buffer.shape[0] and 0 <= j < self.buffer.shape[1]:
            self.buffer[i, j] += energy
