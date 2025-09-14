from dataclasses import dataclass
import numpy as np

@dataclass
class LAD:
    u_bins: np.ndarray
    v_bins: np.ndarray
    mean_dir: np.ndarray
    flux: np.ndarray
    mask_physical: np.ndarray

class LADBuilder:
    def __init__(self, res_u: int = 64, res_v: int = 64, width: float = 0.1, height: float = 0.1):
        self.res_u = res_u; self.res_v = res_v; self.width = width; self.height = height
    def forward_from_LPF(self, nodes_dir: np.ndarray, nodes_energy: np.ndarray) -> LAD:
        u = np.linspace(-self.width/2, self.width/2, self.res_u, dtype=np.float32)
        v = np.linspace(-self.height/2, self.height/2, self.res_v, dtype=np.float32)
        B = self.res_u * self.res_v
        mean_dir = np.zeros((B,3), dtype=np.float32)
        flux = np.zeros((B,), dtype=np.float32)
        mask = np.ones((B,), dtype=np.uint8)
        # Stub: distribute energy uniformly across bins
        if nodes_energy.size > 0:
            flux[:] = nodes_energy.sum() / B
        return LAD(u, v, mean_dir, flux, mask)
