import numpy as np

def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0: 
        return v
    return v / n

def rotation_from_z(to_dir: np.ndarray) -> np.ndarray:
    # minimal rotation aligning z->to_dir
    z = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    v = np.cross(z, to_dir)
    c = np.dot(z, to_dir)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3, dtype=np.float32)
    vx = np.array([[0, -v[2], v[1]],[v[2], 0, -v[0]],[-v[1], v[0], 0]], dtype=np.float32)
    R = np.eye(3, dtype=np.float32) + vx + vx @ vx * (1.0/(1.0 + c))
    return R.astype(np.float32)
