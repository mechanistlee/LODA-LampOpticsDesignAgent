"""광원 소스 스켈레톤.
- 분포/alias-table (미구현) 자리
- AXIS 정렬은 geometry.AxisRegistry 참조 예정
"""
from dataclasses import dataclass
from typing import Dict, Any, Callable
import math

@dataclass
class SampledRay:
    direction: tuple  # (x,y,z)
    energy: float

class SourceBase:
    def sample_direction(self, rng) -> SampledRay:  # placeholder
        return SampledRay((0,0,1), 1.0)

class GaussianSource(SourceBase):
    def __init__(self, fwhm_deg: float):
        self.fwhm = fwhm_deg
        self.sigma = fwhm_deg / (2*math.sqrt(2*math.log(2)))
    def sample_direction(self, rng) -> SampledRay:
        # isotropic fallback
        return SampledRay((0,0,1), 1.0)


def build_source(spec) -> SourceBase:
    if spec.distribution == 'gaussian':
        return GaussianSource(spec.params.get('fwhm_deg', spec.params.get('fwhm', 30)))
    return SourceBase()
