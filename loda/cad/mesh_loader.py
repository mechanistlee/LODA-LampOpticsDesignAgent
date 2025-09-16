
import os
import numpy as np

def load_mesh_any(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.obj', '.stl', '.ply', '.glb', '.gltf'):
        return _load_trimesh(path)
    elif ext in ('.step', '.stp'):
        return _load_step(path)
    else:
        raise ValueError(f"Unsupported format: {ext}")

def _load_trimesh(path):
    import trimesh
    tm = trimesh.load(path, force='mesh')
    if not isinstance(tm, trimesh.Trimesh):
        tm = tm.dump().sum()
    verts = tm.vertices.view(np.ndarray).astype(np.float32)
    faces = tm.faces.view(np.ndarray).astype(np.int32)
    # no labels from file; default -1
    tri_labels = -1 * np.ones(len(faces), dtype=np.int32)
    return {'verts': verts, 'faces': faces, 'tri_labels': tri_labels}

def _load_step(path):
    try:
        from OCC.Core.STEPControl import STEPControl_Reader
        from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopAbs import TopAbs_FACE
        from OCC.Core.BRep import BRep_Tool
        from OCC.Core.gp import gp_Pnt
    except Exception as e:
        raise ImportError("pythonocc-core not available. Install it to load STEP/STP.") from e

    reader = STEPControl_Reader()
    status = reader.ReadFile(path)
    if status != 1:
        raise RuntimeError("STEP read failed")
    reader.TransferRoots()
    shape = reader.OneShape()

    BRepMesh_IncrementalMesh(shape, 0.5, True)
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    verts = []; faces = []
    base = 0
    while exp.More():
        face = exp.Current()
        triangulation = BRep_Tool.Triangulation(face, None)
        if triangulation:
            nodes = triangulation.Nodes()
            tris  = triangulation.Triangles()
            for i in range(1, nodes.Size()+1):
                p: gp_Pnt = nodes.Value(i)
                verts.append((p.X(), p.Y(), p.Z()))
            for i in range(1, tris.Size()+1):
                a,b,c = tris.Value(i).Get()
                faces.append((base+a-1, base+b-1, base+c-1))
            base = len(verts)
        exp.Next()
    verts = np.array(verts, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32)
    tri_labels = -1 * np.ones(len(faces), dtype=np.int32)
    return {'verts': verts, 'faces': faces, 'tri_labels': tri_labels}
