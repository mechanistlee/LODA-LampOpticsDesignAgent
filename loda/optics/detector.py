from dataclasses import dataclass
import numpy as np

@dataclass
class PlanarDetector:
    center: np.ndarray     # (3,)
    normal: np.ndarray     # (3,)
    width: float
    height: float
    res_x: int
    res_y: int

    def __post_init__(self):
        self.normal = self.normal / (np.linalg.norm(self.normal)+1e-12)
        up = np.array([0,0,1], dtype=np.float32) if abs(self.normal[2]) < 0.999 else np.array([1,0,0], dtype=np.float32)
        self.t = np.cross(up, self.normal); self.t /= (np.linalg.norm(self.t)+1e-12)
        self.b = np.cross(self.normal, self.t)
        self.accum = np.zeros((self.res_y, self.res_x), dtype=np.float32)

    def intersect(self, o: np.ndarray, d: np.ndarray):
        denom = float(self.normal @ d)
        if abs(denom) < 1e-8:
            return None
        t = float(((self.center - o) @ self.normal)/denom)
        if t <= 1e-6: 
            return None
        p = o + t*d
        dp = p - self.center
        u = float(dp @ self.t); v = float(dp @ self.b)
        if abs(u) > self.width*0.5 or abs(v) > self.height*0.5:
            return None
        return t, p, u, v

    def add(self, u: float, v: float, power: float):
        i = int((u + self.width*0.5) / self.width * self.res_x)
        j = int((v + self.height*0.5) / self.height * self.res_y)
        i = max(0, min(self.res_x-1, i)); j = max(0, min(self.res_y-1, j))
        self.accum[j, i] += power
