"""Optical property registry.
YAML (opticalproperty.yaml) 로드 & 검증 스켈레톤.
"""
from dataclasses import dataclass
from typing import Dict, Any
import yaml

@dataclass
class SourceSpec:
    name: str
    power: float
    distribution: str
    params: Dict[str, Any]

@dataclass
class SensorSpec:
    name: str
    type: str
    params: Dict[str, Any]

@dataclass
class MaterialSpec:
    name: str
    type: str
    params: Dict[str, Any]

@dataclass
class OpticalRegistry:
    sources: Dict[str, SourceSpec]
    sensors: Dict[str, SensorSpec]
    materials: Dict[str, MaterialSpec]

    @staticmethod
    def load(path: str) -> 'OpticalRegistry':
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        sources = {}
        for k, v in (data.get('sources') or {}).items():
            sources[k] = SourceSpec(k, v.get('power', 1.0), v.get('distribution','uniform'), {kk:vv for kk,vv in v.items() if kk not in ('power','distribution')})
        sensors = {}
        for k, v in (data.get('sensors') or {}).items():
            sensors[k] = SensorSpec(k, v.get('type','planar'), {kk:vv for kk,vv in v.items() if kk not in ('type',)})
        materials = {}
        for k, v in (data.get('materials') or {}).items():
            materials[k] = MaterialSpec(k, v.get('type','dielectric'), {kk:vv for kk,vv in v.items() if kk not in ('type',)})
        return OpticalRegistry(sources, sensors, materials)
