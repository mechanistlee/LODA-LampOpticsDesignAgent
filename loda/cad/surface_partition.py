"""surface_partition.py
표면을 bin 으로 파티셔닝 (스텁 구현)
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Literal, Optional
import numpy as np

def partition_equal_count(faces: np.ndarray, tri_label: np.ndarray, bins: int) -> Dict[int, List[int]]:
    idx = np.arange(faces.shape[0])
    return {i: idx[i::bins].tolist() for i in range(bins)}

def partition_by_label(tri_label: np.ndarray) -> Dict[int, List[int]]:
    out: Dict[int,List[int]] = {}
    for i, lbl in enumerate(tri_label):
        out.setdefault(int(lbl), []).append(i)
    return out

def bin_areas(verts: np.ndarray, faces: np.ndarray, bins: Dict[int,List[int]]) -> Dict[int,float]:
    areas: Dict[int,float] = {}
    v0 = verts[faces[:,0]]; v1 = verts[faces[:,1]]; v2 = verts[faces[:,2]]
    tri_area = 0.5 * np.linalg.norm(np.cross(v1-v0, v2-v0), axis=1)
    for b, lst in bins.items():
        areas[b] = float(tri_area[lst].sum())
    return areas

def partition_equal_area(verts: np.ndarray, faces: np.ndarray, bins: int) -> Dict[int,List[int]]:
    """삼각형 면적 누적 기반 근사 equal-area 분할 (greedy)."""
    if faces.shape[0] == 0 or bins <= 0:
        return {}
    v0 = verts[faces[:,0]]; v1 = verts[faces[:,1]]; v2 = verts[faces[:,2]]
    tri_area = 0.5 * np.linalg.norm(np.cross(v1-v0, v2-v0), axis=1)
    order = np.argsort(-tri_area)
    target = tri_area.sum() / bins
    acc = [0.0]*bins
    bins_out: Dict[int,List[int]] = {i: [] for i in range(bins)}
    for tid in order:
        # 가장 적은 면적 bin 에 추가
        b = int(np.argmin(acc))
        bins_out[b].append(tid)
        acc[b] += tri_area[tid]
    return bins_out

def partition_kmeans(verts: np.ndarray, faces: np.ndarray, k: int, max_iter: int = 20, seed: int = 0) -> Dict[int,List[int]]:
    """단순 k-means (삼각형 중심) 구현 (scikit-learn 없이)."""
    if k <= 0 or faces.shape[0] == 0:
        return {}
    rng = np.random.default_rng(seed)
    v0 = verts[faces[:,0]]; v1 = verts[faces[:,1]]; v2 = verts[faces[:,2]]
    centers = (v0+v1+v2)/3.0
    # 초기 중심
    sel = rng.choice(centers.shape[0], size=min(k, centers.shape[0]), replace=False)
    cent = centers[sel].copy()
    assign = np.zeros(centers.shape[0], dtype=int)
    for _ in range(max_iter):
        # 할당
        d = ((centers[:,None,:]-cent[None,:,:])**2).sum(axis=2)
        new_assign = d.argmin(axis=1)
        if np.all(new_assign == assign):
            break
        assign = new_assign
        for i in range(cent.shape[0]):
            pts = centers[assign==i]
            if pts.size:
                cent[i] = pts.mean(axis=0)
    out: Dict[int,List[int]] = {}
    for i, a in enumerate(assign):
        out.setdefault(int(a), []).append(i)
    return out

__all__ = ['partition_equal_count','partition_by_label','bin_areas','partition_equal_area','partition_kmeans']

__all__ = ['partition_equal_count','partition_by_label','bin_areas']
