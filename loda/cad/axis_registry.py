"""axis_registry.py
Datum Axis 추출 / 보관 구조.
"""
from dataclasses import dataclass
from typing import Dict, Tuple, List

@dataclass
class Axis:
    name: str
    origin: Tuple[float,float,float]
    x: Tuple[float,float,float]
    y: Tuple[float,float,float]
    z: Tuple[float,float,float]

class AxisRegistry:
    def __init__(self):
        self._axes: Dict[str, Axis] = {}

    def add(self, axis: Axis):
        self._axes[axis.name] = axis

    def get(self, name: str) -> Axis:
        return self._axes[name]

    def list(self) -> List[str]:
        return sorted(self._axes.keys())

    def sources(self) -> Dict[str, Axis]:
        return {k:v for k,v in self._axes.items() if k.startswith('AXIS_SOURCE_')}

    def sensors(self) -> Dict[str, Axis]:
        return {k:v for k,v in self._axes.items() if k.startswith('AXIS_SENSOR_')}

__all__ = ['Axis','AxisRegistry']
