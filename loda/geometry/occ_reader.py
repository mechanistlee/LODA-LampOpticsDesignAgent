"""OCC/STEP(XDE) 로더 스켈레톤.

역할:
- STEP -> SceneGraph, AxisRegistry, FaceMap
- 단위/축 정규화

현재는 실제 pythonocc-core 의존성 없이 인터페이스만 제공.
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any

@dataclass
class Axis:
    name: str
    origin: Tuple[float, float, float]
    z: Tuple[float, float, float]
    x: Tuple[float, float, float]
    y: Tuple[float, float, float]

@dataclass
class SceneNode:
    name: str
    transform: List[float]  # 4x4 row-major
    children: List['SceneNode']
    mesh_ref: Optional[str] = None
    label: Optional[str] = None

@dataclass
class SceneGraph:
    root: SceneNode
    faces: Dict[int, str]  # faceId -> label/material key

@dataclass
class AxisRegistry:
    axes: Dict[str, Axis]

class OCCReader:
    def load(self, step_path: str) -> Tuple[SceneGraph, AxisRegistry]:
        # Placeholder: return empty graph
        root = SceneNode(name='ROOT', transform=[1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1], children=[])
        sg = SceneGraph(root=root, faces={})
        reg = AxisRegistry(axes={})
        return sg, reg
