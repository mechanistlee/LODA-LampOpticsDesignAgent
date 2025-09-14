"""Labeling 규칙.
- 이름/색/레이어 -> label 결정
현재 스텁: 단순 이름 기반 매핑.
"""
from typing import Dict

def assign_label(name: str, color: str = '', layer: str = '') -> str:
    if name.upper().startswith('LENS'):
        return 'LENS'
    if 'REFLECT' in name.upper():
        return 'REFLECTOR'
    return name.upper()
