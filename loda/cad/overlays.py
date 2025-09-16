"""overlays.py
축/센서/광선 오버레이 (스텁).
"""
from typing import List, Tuple

def build_axis_polylines(axis_registry, scale: float = 50.0) -> List[List[Tuple[float,float,float]]]:
    lines = []
    for ax in axis_registry.list():  # axis_registry: AxisRegistry
        a = axis_registry.get(ax)
        o = a.origin
        lines.append([o, (o[0]+a.x[0]*scale, o[1]+a.x[1]*scale, o[2]+a.x[2]*scale)])
        lines.append([o, (o[0]+a.y[0]*scale, o[1]+a.y[1]*scale, o[2]+a.y[2]*scale)])
        lines.append([o, (o[0]+a.z[0]*scale, o[1]+a.z[1]*scale, o[2]+a.z[2]*scale)])
    return lines

__all__ = ['build_axis_polylines']
