"""cad_config.py
CAD 관련 전역/프리셋 설정.
"""
from dataclasses import dataclass

@dataclass
class MeshingConfig:
    preset: str = 'medium'  # fast|medium|quality
    linear_deflection_fast: float = 1.0
    linear_deflection_medium: float = 0.5
    linear_deflection_quality: float = 0.2
    angular_deflection_fast: float = 10.0
    angular_deflection_medium: float = 5.0
    angular_deflection_quality: float = 2.0

    def resolve(self):
        if self.preset == 'fast':
            return self.linear_deflection_fast, self.angular_deflection_fast
        if self.preset == 'quality':
            return self.linear_deflection_quality, self.angular_deflection_quality
        return self.linear_deflection_medium, self.angular_deflection_medium

@dataclass
class OverlayConfig:
    axis_length: float = 50.0  # mm
    ray_opacity: float = 0.8
    axis_thickness: float = 2.0

@dataclass
class CADConfig:
    meshing: MeshingConfig = MeshingConfig()
    overlay: OverlayConfig = OverlayConfig()
    cache_dir: str = '.cad_cache'
    enable_cache: bool = True

__all__ = ['CADConfig','MeshingConfig','OverlayConfig']
