"""geometry_info.py
기하 메타데이터 및 쿼리 API 스켈레톤.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Dict, Any
import numpy as np

@dataclass
class AABB:
    min: Tuple[float,float,float]
    max: Tuple[float,float,float]

def compute_aabb(verts: np.ndarray) -> AABB:
    if verts.size == 0:
        return AABB((0,0,0),(0,0,0))
    mn = verts.min(axis=0)
    mx = verts.max(axis=0)
    return AABB(tuple(mn), tuple(mx))

def centroid(verts: np.ndarray) -> Tuple[float,float,float]:
    if verts.size == 0:
        return (0.0,0.0,0.0)
    c = verts.mean(axis=0)
    return float(c[0]), float(c[1]), float(c[2])

def surface_area(verts: np.ndarray, faces: np.ndarray) -> float:
    if faces.size == 0:
        return 0.0
    v0 = verts[faces[:,0]]
    v1 = verts[faces[:,1]]
    v2 = verts[faces[:,2]]
    return float(0.5 * np.linalg.norm(np.cross(v1-v0, v2-v0), axis=1).sum())

def geometry_summary(verts: np.ndarray, faces: np.ndarray) -> Dict[str,Any]:
    aabb = compute_aabb(verts)
    return {
        'verts': int(verts.shape[0]),
        'faces': int(faces.shape[0]),
        'aabb_min': aabb.min,
        'aabb_max': aabb.max,
        'area': surface_area(verts, faces),
        'centroid': centroid(verts)
    }

__all__ = ['AABB','compute_aabb','centroid','surface_area','geometry_summary']
