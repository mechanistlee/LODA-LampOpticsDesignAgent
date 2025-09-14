"""3D Surface-bin Sensor 스켈레톤.
메쉬 face 기반 binning, 각도 히스토그램 누적.
"""
from dataclasses import dataclass
from typing import Dict, Any, Tuple
import numpy as np
import math

@dataclass
class SurfaceBin:
    face_indices: Tuple[int, ...]
    normal: Tuple[float, float, float]
    area: float

class SurfaceBinSensor:
    def __init__(self, bins: Dict[int, SurfaceBin], theta_bins: int = 36, phi_bins: int = 72):
        self.bins = bins
        self.theta_bins = theta_bins
        self.phi_bins = phi_bins
        self.hist = {bid: np.zeros((theta_bins, phi_bins), dtype=np.float32) for bid in bins}
        self.energy_sum = {bid: 0.0 for bid in bins}

    def accumulate(self, bin_id: int, dir_local: Tuple[float,float,float], energy: float):
        # dir_local 은 (n,t,b) 프레임 기준
        x,y,z = dir_local
        # 반구 판단: z>0만 유지
        if z <= 0:
            return
        theta = math.acos(max(-1.0, min(1.0, z)))  # 0~pi/2
        phi = math.atan2(y, x)
        if phi < 0:
            phi += 2*math.pi
        ti = int(theta / (0.5*math.pi) * self.theta_bins)
        pi = int(phi / (2*math.pi) * self.phi_bins)
        if ti >= self.theta_bins:
            ti = self.theta_bins - 1
        if pi >= self.phi_bins:
            pi = self.phi_bins - 1
        if bin_id in self.hist:
            self.hist[bin_id][ti, pi] += energy
            self.energy_sum[bin_id] += energy

    def to_sensor_source(self, bin_id: int) -> Dict[str, Any]:
        h = self.hist[bin_id]
        total = h.sum()
        if total <= 0:
            prob = h
        else:
            prob = h / total
        return {
            'bin_id': bin_id,
            'prob': prob,
            'energy_sum': self.energy_sum[bin_id]
        }
