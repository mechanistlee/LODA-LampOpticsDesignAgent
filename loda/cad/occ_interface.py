"""occ_interface.py
STEP/XDE 로드 및 기본 파이프라인 진입점.
pythonocc-core 미존재 환경에서도 인터페이스 임포트 가능하도록 지연로드 패턴.
"""
from __future__ import annotations
from typing import Tuple, Dict, Any, Optional
import os, logging, hashlib
from .cad_config import CADConfig
from .axis_registry import AxisRegistry
from . import labeling
from . import meshing as legacy_meshing  # 기존 호환
from .cad_logging import summarize_load

log = logging.getLogger('loda.cad.occ')

class StepLoadResult:
    def __init__(self, scene_graph, axis_registry: AxisRegistry, face_map: Dict[int, Any], meta: Dict[str,Any]):
        self.scene_graph = scene_graph
        self.axis_registry = axis_registry
        self.face_map = face_map
        self.meta = meta

class OCCInterface:
    def __init__(self, config: Optional[CADConfig] = None):
        self.config = config or CADConfig()
        self._has_occ = self._detect_occ()
        if not self._has_occ:
            log.info("pythonocc-core not detected: running in fallback mode (axis text scan only).")

    def _detect_occ(self) -> bool:
        try:  # pragma: no cover
            import OCC.Core  # noqa: F401
            return True
        except Exception:
            return False

    def load_step(self, step_path: str) -> StepLoadResult:
        if not os.path.isfile(step_path):
            raise FileNotFoundError(step_path)
        if self._has_occ:
            return self._load_with_occ(step_path)
        return self._fallback(step_path)

    # ---------------- Fallback ---------------- #
    def _fallback(self, step_path: str) -> StepLoadResult:
        # 간단 축 패턴만 스캔 -> axis_registry
        from .occ_reader import OCCReader  # 재사용
        reader = OCCReader()
        sg, axis_reg, faces = reader.load(step_path)
        meta = {
            'units': 'mm', 'nodes': 1, 'faces': 0, 'axes': len(axis_reg.axes), 'mode': 'fallback'
        }
        summarize_load(step_path, meta)
        return StepLoadResult(sg, axis_reg, faces, meta)

    # ---------------- OCC Real (Stub) ---------------- #
    def _load_with_occ(self, step_path: str) -> StepLoadResult:  # pragma: no cover - requires OCC
        """실제 OCC 경로 스켈레톤.

        의도된 흐름:
        1) STEPCAFControl_Reader 로드 -> Transfer -> XDE 라벨 트리 획득
        2) ShapeTool, ColorTool, LayerTool, MaterialTool 접근
        3) 어셈블리 DFS: 각 라벨의 Name / 색 / Layer / Material → node 구성
        4) 개별 기하(Part) Shape 에 메싱 수행 (meshing.mesh_shape)
        5) Face 순회하여 label key (이름 규칙 + 색/레이어) 생성 → face_map
        6) AxisRegistry: DatumAxis or 이름 패턴(AXIS_SOURCE_*, AXIS_SENSOR_*) 필터링
        7) meta 수집 (units, faces, nodes, axes)
        현재는 세부 구현 미포함: 최소한 구조 dict 반환.
        """
        try:
            from OCC.Core.STEPCAFControl import STEPCAFControl_Reader  # type: ignore
            from OCC.Core.XCAFApp import XCAFApp_Application  # type: ignore
            from OCC.Core.TDocStd import TDocStd_Document  # type: ignore
            from OCC.Core.TCollection import TCollection_ExtendedString  # type: ignore
            from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool  # type: ignore
            from OCC.Core.TDF import TDF_LabelSequence  # type: ignore
        except Exception:
            log.warning("OCC modules missing at runtime despite detection flag; fallback.")
            return self._fallback(step_path)

        # 1) Reader 준비
        reader = STEPCAFControl_Reader()
        status = reader.ReadFile(step_path)
        if status != 1:  # IFSelect_RetDone == 1
            raise RuntimeError(f"STEP load failed status={status}")
        if not reader.Transfer():  # XDE 전송
            raise RuntimeError("STEP Transfer failed")
        doc = reader.Document()
        shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())
        color_tool = XCAFDoc_DocumentTool.ColorTool(doc.Main())
        layer_tool = XCAFDoc_DocumentTool.LayerTool(doc.Main())

        # 2) 루트 라벨들
        roots = TDF_LabelSequence()
        shape_tool.GetFreeShapes(roots)

        nodes = []
        face_map = {}
        node_count = 0
        face_count = 0

        def traverse(label, parent_path: str):  # pragma: no cover - requires OCC
            nonlocal node_count, face_count
            name = shape_tool.GetShapeLabel(label).Tag() if label.IsNull() else shape_tool.GetShape(label)
            try:
                from OCC.Core.TDataStd import TDataStd_Name  # type: ignore
                if TDataStd_Name.IsAssigned(label):
                    name_attr = TDataStd_Name.Get(label)
                    name_str = name_attr.Get().ToExtString()
                else:
                    name_str = f"NODE_{node_count}"
            except Exception:
                name_str = f"NODE_{node_count}"
            node_path = parent_path + '/' + name_str if parent_path else name_str
            node_count += 1
            # TODO: 색, 레이어 조회 -> color_tool, layer_tool
            # TODO: shape = shape_tool.GetShape(label) -> meshing
            # TODO: faces 추출 후 face_map[face_id] = {'label': labeling.assign_label(name_str, ...)}
            # TODO: children 재귀 (GetComponents)
            return

        for i in range(1, roots.Length()+1):  # pragma: no cover
            traverse(roots.Value(i), '')

        # Axis 추출 placeholder
        axis_reg = AxisRegistry()

        meta = {'units':'mm','nodes':node_count,'faces':face_count,'axes':len(axis_reg.list()),'mode':'occ'}
        summarize_load(step_path, meta)
        # 임시: 기존 간단 구조 재사용 (occ_reader) -> 얼굴/축 정보는 fallback 결과와 동일
        from .occ_reader import OCCReader
        sg, axis_reg2, faces2 = OCCReader().load(step_path)
        return StepLoadResult(sg, axis_reg2, faces2, meta)

__all__ = ['OCCInterface','StepLoadResult']
