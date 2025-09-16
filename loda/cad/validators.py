"""validators.py
단위/좌표계/법선 검사 및 보정 스켈레톤.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, Any, Optional, Tuple

def assert_standard_frame(meta: Dict[str,Any]):
    """프로젝트 표준 (mm, RHS, Z-up) 여부 확인.
    meta 예상 키: units, handedness, up_axis
    """
    u = meta.get('units')
    if u not in ('mm','millimeter','millimetre'):
        raise ValueError(f"Unexpected length unit: {u}")
    if meta.get('handedness','RHS') != 'RHS':
        raise ValueError("Non-right-handed coordinate system detected")
    if meta.get('up_axis','Z') != 'Z':
        raise ValueError("Up axis not Z")

def fix_normals(verts: np.ndarray, faces: np.ndarray, normals: np.ndarray,
                reference_dir: Optional[Tuple[float,float,float]] = None) -> np.ndarray:
    """법선 방향 뒤집힘 보정.

    전략:
    1. 삼각형 중심 c_i 계산
    2. 기준 벡터 ref 선택: reference_dir 제공 시 정규화 후 사용, 아니면 (c_i - scene_centroid)
    3. n_i · ref < 0 인 경우 n_i 반전

    Parameters
    ----------
    verts : (N,3)
    faces : (F,3)
    normals : (F,3) 초기 삼각형 노멀 (정규화 가정)
    reference_dir : 글로벌 기준 (옵션)
    """
    if faces.size == 0:
        return normals
    v0 = verts[faces[:,0]]; v1 = verts[faces[:,1]]; v2 = verts[faces[:,2]]
    centers = (v0+v1+v2)/3.0
    if reference_dir is not None:
        import math
        ref = np.array(reference_dir, dtype=float)
        l = np.linalg.norm(ref) or 1.0
        ref /= l
        dots = (normals @ ref)
        flip = dots < 0.0
        normals[flip] *= -1.0
        return normals
    scene_c = centers.mean(axis=0)
    vec = centers - scene_c
    lens = np.linalg.norm(vec, axis=1)
    mask = lens > 0
    vec[mask] /= lens[mask][:,None]
    dots = (normals[mask]*vec[mask]).sum(axis=1)
    flip_idx = np.where(dots < 0.0)[0]
    # map back to full normals indices
    full_indices = np.where(mask)[0][flip_idx]
    normals[full_indices] *= -1.0
    return normals

__all__ = ['assert_standard_frame','fix_normals']
