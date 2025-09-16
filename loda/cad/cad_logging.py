"""cad_logging.py
CAD 파이프라인 로깅 유틸.
"""
from __future__ import annotations
import logging, json
from typing import Dict, Any

log = logging.getLogger('loda.cad')

def summarize_load(step_path: str, meta: Dict[str, Any]):
    log.info("[CAD] STEP Load: path=%s units=%s nodes=%d faces=%d axes=%d", step_path, meta.get('units'), meta.get('nodes'), meta.get('faces'), meta.get('axes'))

def summarize_bake(meta: Dict[str, Any]):
    log.info("[CAD] Bake: verts=%d faces=%d unique_labels=%d area_total=%.3f", meta.get('verts'), meta.get('faces'), meta.get('labels'), meta.get('area_total', 0.0))

def debug_json(tag: str, obj: Any):  # pragma: no cover - optional debug
    log.debug("[CAD][%s] %s", tag, json.dumps(obj, ensure_ascii=False, indent=2, default=str))

__all__ = ['summarize_load','summarize_bake','debug_json']
