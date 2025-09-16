"""meshing.py
OCC BRep 메싱 래퍼 (스켈레톤) + numpy 변환 유틸.
pythonocc-core 설치 이전 환경에서도 임포트 가능.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, Any
import logging
import numpy as np

log = logging.getLogger('loda.cad.meshing')

@dataclass
class MeshingPreset:
    name: str
    linear_deflection: float
    angular_deflection_deg: float
    relative: bool = False  # OCC IncrementalMesh relative deflection

PRESETS: Dict[str, MeshingPreset] = {
    'fast': MeshingPreset('fast', 1.0, 10.0),
    'medium': MeshingPreset('medium', 0.5, 5.0),
    'quality': MeshingPreset('quality', 0.2, 2.0)
}

def get_preset(name: str) -> MeshingPreset:
    return PRESETS.get(name, PRESETS['medium'])

def mesh_shape(shape, preset: MeshingPreset) -> Dict[str, Any]:  # pragma: no cover - requires OCC
    """단일 TopoDS_Shape 메싱 후 numpy array 로 변환.
    Returns dict with keys: verts (Nx3), faces (Mx3)
    """
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopAbs import TopAbs_FACE
    from OCC.Core.TopoDS import topods_Face
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.Poly import Poly_Triangulation

    lin = preset.linear_deflection
    ang = np.deg2rad(preset.angular_deflection_deg)
    BRepMesh_IncrementalMesh(shape, lin, preset.relative, ang, True)

    verts_acc = []
    faces_acc = []
    vert_offset = 0

    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = topods_Face(exp.Current())
        loc = face.Location()
        triangulation = BRep_Tool.Triangulation(face, loc)
        if triangulation is None:
            exp.Next(); continue
        # Extract points
        pts = triangulation.Nodes()
        arr = np.array([[pts.Value(i).X(), pts.Value(i).Y(), pts.Value(i).Z()] for i in range(1, pts.Length()+1)], dtype=float)
        tris = triangulation.Triangles()
        tri_idx = []
        for i in range(1, tris.Length()+1):
            t = tris.Value(i)
            n1, n2, n3 = t.Get()
            tri_idx.append([n1-1+vert_offset, n2-1+vert_offset, n3-1+vert_offset])
        verts_acc.append(arr)
        faces_acc.append(np.array(tri_idx, dtype=int))
        vert_offset += arr.shape[0]
        exp.Next()

    if not verts_acc:
        return {'verts': np.zeros((0,3)), 'faces': np.zeros((0,3), dtype=int)}
    verts = np.vstack(verts_acc)
    faces = np.vstack(faces_acc)
    return {'verts': verts, 'faces': faces}

__all__ = ['MeshingPreset','get_preset','mesh_shape']

