"""Meshing preset 스켈레톤.
허용오차(deflection) 및 품질 프리셋 정의.
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class MeshingPreset:
    name: str
    linear_deflection: float
    angular_deflection_deg: float

PRESETS: Dict[str, MeshingPreset] = {
    'fast': MeshingPreset('fast', 1.0, 10.0),
    'medium': MeshingPreset('medium', 0.5, 5.0),
    'quality': MeshingPreset('quality', 0.2, 2.0)
}

def get_preset(name: str) -> MeshingPreset:
    return PRESETS.get(name, PRESETS['medium'])
