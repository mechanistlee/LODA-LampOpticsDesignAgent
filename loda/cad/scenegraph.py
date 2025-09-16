"""scenegraph.py
SceneGraph 구성 및 베이크(flat mesh) 도구.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np

@dataclass
class SceneNode:
    name: str
    transform: np.ndarray  # (4,4)
    children: List['SceneNode']
    mesh: Optional['MeshData'] = None
    label: Optional[str] = None

@dataclass
class MeshData:
    verts: np.ndarray  # (N,3)
    faces: np.ndarray  # (M,3) int
    tri_label: Optional[np.ndarray] = None  # (M,) str or int label indices

@dataclass
class BakedMesh:
    verts: np.ndarray
    faces: np.ndarray
    tri_label: np.ndarray  # (F,)
    label_map: Dict[int, str]  # index -> label string
    reverse_index: Dict[int, Tuple[str,str]]  # tri_index -> (node_path,label)

def bake(root: SceneNode) -> BakedMesh:
    verts_list = []
    faces_list = []
    labels_list = []
    label_map: Dict[int,str] = {}
    label_to_index: Dict[str,int] = {}
    reverse_index: Dict[int,Tuple[str,str]] = {}
    vert_offset = 0
    tri_global_index = 0

    def traverse(node: SceneNode, path: List[str]):
        nonlocal vert_offset, tri_global_index
        node_path = '/'.join(path + [node.name])
        if node.mesh is not None:
            v = (node.transform @ np.hstack([node.mesh.verts, np.ones((node.mesh.verts.shape[0], 1))]).T).T[:, :3]
            f = node.mesh.faces + vert_offset
            verts_list.append(v)
            faces_list.append(f)
            if node.mesh.tri_label is not None:
                for local_i, lbl in enumerate(node.mesh.tri_label):
                    lbl_str = str(lbl)
                    if lbl_str not in label_to_index:
                        label_to_index[lbl_str] = len(label_to_index) + 1  # 0 reserved
                        label_map[label_to_index[lbl_str]] = lbl_str
                    idx = label_to_index[lbl_str]
                    labels_list.append(idx)
                    reverse_index[tri_global_index] = (node_path, lbl_str)
                    tri_global_index += 1
            else:
                for _ in range(node.mesh.faces.shape[0]):
                    labels_list.append(0)
                    reverse_index[tri_global_index] = (node_path, node.label or 'UNLABELED')
                    tri_global_index += 1
            vert_offset += v.shape[0]
        for child in node.children:
            traverse(child, path + [node.name])
    traverse(root, [])
    if not verts_list:
        return BakedMesh(np.zeros((0,3)), np.zeros((0,3),dtype=int), np.zeros((0,),dtype=int), {}, {})
    verts = np.vstack(verts_list)
    faces = np.vstack(faces_list).astype(int)
    tri_label = np.array(labels_list, dtype=int)
    return BakedMesh(verts, faces, tri_label, label_map, reverse_index)

__all__ = ['SceneNode','MeshData','BakedMesh','bake']
