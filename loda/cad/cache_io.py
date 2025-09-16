"""cache_io.py
메싱/베이크 결과 캐시 (npz).
"""
from __future__ import annotations
import os, json, hashlib
from typing import Tuple, Optional, Dict, Any
import numpy as np

def _hash_key(step_path: str, preset: str, extra: str = '') -> str:
    st = os.stat(step_path)
    h = hashlib.sha256()
    h.update(step_path.encode())
    h.update(str(st.st_mtime_ns).encode())
    h.update(preset.encode())
    if extra:
        h.update(extra.encode())
    return h.hexdigest()[:20]

def cache_paths(cache_dir: str, hash_id: str) -> Tuple[str,str]:
    return (os.path.join(cache_dir, f"{hash_id}.npz"), os.path.join(cache_dir, f"{hash_id}.meta.json"))

def save_mesh_cache(cache_dir: str, hash_id: str, verts, faces, tri_label, meta: Dict[str,Any]):
    os.makedirs(cache_dir, exist_ok=True)
    np.savez_compressed(os.path.join(cache_dir, f"{hash_id}.npz"), verts=verts, faces=faces, tri_label=tri_label)
    with open(os.path.join(cache_dir, f"{hash_id}.meta.json"), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def load_mesh_cache(cache_dir: str, hash_id: str, expected_units: str = 'mm', expected_preset: str = '') -> Optional[Tuple[np.ndarray,np.ndarray,np.ndarray,Dict[str,Any]]]:
    npz_path, meta_path = cache_paths(cache_dir, hash_id)
    if not (os.path.isfile(npz_path) and os.path.isfile(meta_path)):
        return None
    data = np.load(npz_path)
    with open(meta_path,'r',encoding='utf-8') as f:
        meta = json.load(f)
    # 메타 검증: units / preset 일치하지 않으면 miss 취급
    if expected_units and meta.get('units') and meta.get('units') != expected_units:
        return None
    if expected_preset and meta.get('preset') and meta.get('preset') != expected_preset:
        return None
    return data['verts'], data['faces'], data['tri_label'], meta

__all__ = ['_hash_key','cache_paths','save_mesh_cache','load_mesh_cache']
