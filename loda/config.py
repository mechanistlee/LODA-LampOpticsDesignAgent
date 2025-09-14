from typing import Tuple
from dataclasses import dataclass
import os
from typing import List, Tuple, Optional

@dataclass
class Config:
    # Global units: meters, watts, steradians
    seed: int = 42
    device: str = "cpu"
    # Output paths
    out_dir: str = "/mnt/data/loda_out"
    optical_property_yaml: str = "loda/optics/opticalproperty.yaml"
    optix_enabled: bool = False  # 실제 OptiX 연동 시 True
    optix_max_bounces: int = 4
    optix_wavefront: bool = True
    mm_to_m: float = 0.001


# ---- LPFConfig: Light Path Field 설정 ----
from dataclasses import dataclass

@dataclass
class LPFConfig:
    source_angle: float = 120.0    # degrees
    ray_resolution: float = 10.0   # degrees
    bounces: int = 2               # >=1
    source_origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    def compute_size(self) -> Tuple[int, int]:
        import math
        if not (1 <= self.source_angle <= 180):
            raise ValueError("source_angle must be in [1,180]")
        if not (0.001 <= self.ray_resolution <= 20):
            raise ValueError("ray_resolution must be in [0.001,20]")
        size = int(math.floor(self.source_angle / self.ray_resolution) + 1)
        return size, size

