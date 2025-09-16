
import numpy as np

class SceneNode:
    def __init__(self, name, transform=None, mesh=None, label=None):
        self.name = name
        self.transform = np.eye(4, dtype=np.float64) if transform is None else transform
        self.mesh = mesh  # dict: {'verts':(N,3) float32, 'faces':(M,3) int32, 'tri_labels':(M,) optional}
        self.label = label
        self.children = []

class Axis:
    def __init__(self, name, origin, x, y, z):
        self.name = name
        self.origin = np.array(origin, dtype=np.float64)
        self.x = np.array(x, dtype=np.float64)
        self.y = np.array(y, dtype=np.float64)
        self.z = np.array(z, dtype=np.float64)

class SceneGraph:
    def __init__(self, root, axes):
        self.root = root
        self.axes = {a.name: a for a in axes}

    def find_axis(self, name):
        return self.axes.get(name, None)

def aabb_from_mesh(mesh):
    v = mesh['verts']
    return v.min(axis=0), v.max(axis=0)
