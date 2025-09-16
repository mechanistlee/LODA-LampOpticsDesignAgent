"""colormaps.py
라벨/재질 → 색상 매핑.
"""
from typing import Tuple, Dict

DEFAULT_MATERIAL_COLORS: Dict[str, Tuple[float,float,float]] = {
    'LENS': (0.6, 0.8, 1.0),
    'REFLECTOR': (0.9, 0.9, 0.9),
    'SOURCE': (1.0, 0.7, 0.2),
    'SENSOR': (0.2, 1.0, 0.2),
    'DEFAULT': (0.8, 0.8, 0.8)
}

def color_for(label: str) -> Tuple[float,float,float]:
    return DEFAULT_MATERIAL_COLORS.get(label.upper(), DEFAULT_MATERIAL_COLORS['DEFAULT'])

__all__ = ['color_for','DEFAULT_MATERIAL_COLORS']
