"""OCC/STEP(XDE) 로더 (설계 중심 스켈레톤).

목표 기능 (현재 파일은 pythonocc-core 없이도 임포트 가능하도록 "지연 의존성" 패턴 사용):
1. STEP(XDE) -> SceneGraph, AxisRegistry, FaceMap(FaceInfo)
2. 계층/이름/색/레이어 유지, 단위(mm) 및 우수좌표(RHS) 정규화
3. 축/로컬좌표계 자동 추출 (이름 규칙: AXIS_SOURCE_*, AXIS_SENSOR_*)
4. 메싱 프리셋 (fast/medium/quality) 의 허용오차(deflection) 적용
5. 가시화 어댑터 (PyVista/Open3D) 스텁: 디버깅용 폴리라인(LPF 경로) 오버레이 염두
6. 면 라벨 안정성: face index + (name/color/layer 기반 label) 병행 저장

실 구현시 확장 포인트(TODO 태그):
 - _load_xde: STEPCAFControl_Reader & TDF_LabelTree 순회, name/color/material 추출
 - _triangulate_shape: BRepMesh_IncrementalMesh 수행 후 TopExp_Explorer + TopoDS_Face -> Triangulation
 - _extract_axes_from_shapes: 사용자 정의 DATUM / AXIS geometry 지원 (Geom_Axis2Placement)
 - _compute_normals: OCC triangulation normal 보정 (뒤집힘 시 dot(outward_ref) < 0 -> flip)
 - _unit_detection: STEP 파일 내 단위(Length_Unit) 파싱

Fallback 전략:
 - pythonocc-core 미설치: 텍스트 라인 스캐닝으로 AXIS_* 패턴만 추출, 빈 SceneGraph 반환
 - 가시화 라이브러리 미설치: 어댑터 메서드 호출 시 NotImplementedError 안내

Interface 계약:
OCCReader.load(step_path: str, meshing: str='medium') -> (SceneGraph, AxisRegistry, FaceMap)

개발 편의를 위해 FaceMap 을 SceneGraph.faces 와 별개 구조로 보관하되 반환시 dict 로 노출.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Iterable
import re
import math
import logging
from .meshing import get_preset, MeshingPreset
from .labeling import assign_label

log = logging.getLogger(__name__)

# ------------------------- Data Model ------------------------- #

IDENTITY_4x4 = [1.0,0.0,0.0,0.0,
                0.0,1.0,0.0,0.0,
                0.0,0.0,1.0,0.0,
                0.0,0.0,0.0,1.0]

@dataclass
class Axis:
    name: str
    origin: Tuple[float, float, float]
    z: Tuple[float, float, float]
    x: Tuple[float, float, float]
    y: Tuple[float, float, float]

@dataclass
class FaceInfo:
    face_id: int
    label: str
    material_key: str
    color: Optional[Tuple[float, float, float]] = None
    layer: Optional[str] = None
    area: Optional[float] = None
    mesh_ref: Optional[str] = None  # key for mesh storage map

@dataclass
class SceneNode:
    name: str
    transform: List[float]  # 4x4 row-major
    children: List['SceneNode'] = field(default_factory=list)
    mesh_ref: Optional[str] = None
    label: Optional[str] = None

@dataclass
class SceneGraph:
    root: SceneNode
    faces: Dict[int, FaceInfo]

@dataclass
class AxisRegistry:
    axes: Dict[str, Axis]
    def find(self, prefix: str) -> Dict[str, Axis]:
        return {k: v for k, v in self.axes.items() if k.startswith(prefix)}


class VisualizationAdapter:
    """가시화 어댑터 스텁.

    실제 구현시:
        - to_pyvista(scene_graph) -> pyvista.Plotter 객체 반환 (optional)
        - overlay_paths(plotter, list_of_polyline_points)
    현재는 라이브러리 미존재시 예외 발생.
    """
    def __init__(self):
        self._pv_available = False
        self._o3d_available = False
        try:
            import pyvista  # noqa: F401
            self._pv_available = True
        except Exception:  # pragma: no cover
            pass
        try:
            import open3d  # noqa: F401
            self._o3d_available = True
        except Exception:  # pragma: no cover
            pass

    def ensure_pyvista(self):
        if not self._pv_available:
            raise NotImplementedError("PyVista not installed. Add 'pyvista' to requirements (optional).")

    def ensure_o3d(self):
        if not self._o3d_available:
            raise NotImplementedError("Open3D not installed. Add 'open3d' to requirements (optional).")

    # Placeholder methods
    def to_pyvista(self, scene_graph: SceneGraph):  # pragma: no cover - stub
        self.ensure_pyvista()
        raise NotImplementedError

    def overlay_paths(self, plotter, polylines: List[List[Tuple[float,float,float]]]):  # pragma: no cover - stub
        self.ensure_pyvista()
        raise NotImplementedError


# ------------------------- Core Reader ------------------------- #

class OCCReader:
    def __init__(self, mm_to_m: float = 0.001):
        self.mm_to_m = mm_to_m
        self._has_occ = self._detect_occ()
        if not self._has_occ:
            log.info("pythonocc-core not detected; OCCReader will operate in fallback mode (axes text scan only).")

    # Public API
    def load(self, step_path: str, meshing: str = 'medium') -> Tuple[SceneGraph, AxisRegistry, Dict[int, FaceInfo]]:
        """STEP(XDE) 파일 로드.

        Parameters
        ----------
        step_path : str
            입력 STEP(.stp/.step).
        meshing : str
            'fast' | 'medium' | 'quality'. pythonocc-core 설치 전에는 영향 없음.

        Returns
        -------
        (SceneGraph, AxisRegistry, FaceMap) 튜플
        """
        preset = get_preset(meshing)
        if self._has_occ:
            return self._load_with_occ(step_path, preset)
        else:
            return self._fallback_parse(step_path)

    # --------------------- OCC Implementation (stubs) --------------------- #
    def _load_with_occ(self, step_path: str, preset: MeshingPreset) -> Tuple[SceneGraph, AxisRegistry, Dict[int, FaceInfo]]:
        """실제 OCC 파이프라인 (현재는 스켈레톤)."""
        try:  # pragma: no cover - executed only when occ installed
            # 1) Load XDE (names/colors/hierarchy)
            xde_root = self._load_xde(step_path)
            # 2) Build SceneGraph nodes (transform propagation)
            root_node = self._build_scene_graph(xde_root)
            # 3) Triangulate & collect faces
            faces = self._collect_faces(xde_root, preset)
            # 4) Unit normalization (STEP 내부 단위 확인 후 mm->m 변환)
            self._normalize_units(root_node, faces)
            # 5) Extract axes
            axis_reg = self._extract_axes_from_labels(faces.keys(), xde_root)
            scene_graph = SceneGraph(root=root_node, faces=faces)
            return scene_graph, axis_reg, faces
        except Exception as e:  # pragma: no cover
            log.exception("OCC pipeline failed; falling back to text scan mode: %s", e)
            return self._fallback_parse(step_path)

    def _load_xde(self, step_path: str):  # pragma: no cover - skeleton
        """STEPCAFControl_Reader 사용하여 XDE 로드 (스켈레톤)."""
        # 실제 구현시: STEPCAFControl_Reader -> reader.ReadFile -> Transfer
        # 반환: 루트 TDF_Label 혹은 커스텀 래퍼
        raise NotImplementedError

    def _build_scene_graph(self, xde_root) -> SceneNode:  # pragma: no cover - skeleton
        # TODO: XCAFDoc_ShapeTool 순회 -> 어셈블리 계층
        return SceneNode(name='ROOT', transform=IDENTITY_4x4)

    def _collect_faces(self, xde_root, preset: MeshingPreset) -> Dict[int, FaceInfo]:  # pragma: no cover - skeleton
        # TODO: 각 Shape -> Triangulation 수행 후 face id/label/color 추출
        return {}

    def _normalize_units(self, root_node: SceneNode, faces: Dict[int, FaceInfo]):  # pragma: no cover - skeleton
        # TODO: STEP length unit 가져와 mm 정의 아니면 비율을 곱해 변환
        pass

    def _extract_axes_from_labels(self, face_ids: Iterable[int], xde_root) -> AxisRegistry:  # pragma: no cover - skeleton
        # TODO: Datum / Axis shapes or label naming
        return AxisRegistry(axes={})

    # --------------------- Fallback Text Parsing --------------------- #
    AXIS_PATTERN = re.compile(r'(AXIS_(?:SOURCE|SENSOR)_[A-Za-z0-9_]+)\s*[:=]\s*\(?([0-9eE+\-. ,]+)\)?')
    # 허용 포맷 예: AXIS_SOURCE_LED1:(0,0,0;0,0,1;1,0,0)
    # origin;z;x 3개 세미콜론 구분 (y는 z×x 자동생성)

    def _fallback_parse(self, step_path: str) -> Tuple[SceneGraph, AxisRegistry, Dict[int, FaceInfo]]:
        axes: Dict[str, Axis] = {}
        try:
            with open(step_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            for m in self.AXIS_PATTERN.finditer(text):
                name, vec_block = m.group(1), m.group(2)
                parts = re.split(r'[;]', vec_block)
                if len(parts) >= 3:
                    o = self._parse_vec(parts[0])
                    z = self._normalize(self._parse_vec(parts[1]))
                    x = self._normalize(self._parse_vec(parts[2]))
                    y = self._normalize(self._cross(z, x))
                    axes[name] = Axis(name=name, origin=o, z=z, x=x, y=y)
        except FileNotFoundError:
            log.warning("STEP file not found in fallback parse: %s", step_path)
        root = SceneNode(name='ROOT', transform=IDENTITY_4x4)
        scene_graph = SceneGraph(root=root, faces={})
        axis_reg = AxisRegistry(axes=axes)
        return scene_graph, axis_reg, {}

    # --------------------- Math Helpers --------------------- #
    @staticmethod
    def _parse_vec(s: str) -> Tuple[float,float,float]:
        nums = re.split(r'[ ,]+', s.strip().strip('()'))
        vals = [float(n) for n in nums if n]
        while len(vals) < 3:
            vals.append(0.0)
        return vals[0], vals[1], vals[2]

    @staticmethod
    def _normalize(v: Tuple[float,float,float]) -> Tuple[float,float,float]:
        l = math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]) or 1.0
        return (v[0]/l, v[1]/l, v[2]/l)

    @staticmethod
    def _cross(a: Tuple[float,float,float], b: Tuple[float,float,float]) -> Tuple[float,float,float]:
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

    # --------------------- Future Utility APIs --------------------- #
    def export_axis_registry(self, axis_reg: AxisRegistry) -> Dict[str, Dict[str, Tuple[float,float,float]]]:
        return {k: { 'origin': v.origin, 'z': v.z, 'x': v.x, 'y': v.y } for k,v in axis_reg.axes.items()}

    def list_source_axes(self, axis_reg: AxisRegistry) -> List[str]:
        return sorted([k for k in axis_reg.axes if k.startswith('AXIS_SOURCE_')])

    def list_sensor_axes(self, axis_reg: AxisRegistry) -> List[str]:
        return sorted([k for k in axis_reg.axes if k.startswith('AXIS_SENSOR_')])

__all__ = [
    'Axis','FaceInfo','SceneNode','SceneGraph','AxisRegistry','VisualizationAdapter','OCCReader'
]
