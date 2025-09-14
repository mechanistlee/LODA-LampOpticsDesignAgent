from dataclasses import dataclass
import numpy as np
from .losses import RPALosses

@dataclass
class RPAConfig:
    step_size: float = 0.1

class RPA:
    def __init__(self, cfg: RPAConfig):
        self.cfg = cfg
    def step(self, nodes_dir: np.ndarray, axis: np.ndarray) -> tuple[np.ndarray, RPALosses, dict]:
        # Nudge directions toward axis (simple heuristic demo)
        axis = axis / (np.linalg.norm(axis)+1e-12)
        new_dirs = (1-self.cfg.step_size)*nodes_dir + self.cfg.step_size*axis[None,:]
        new_dirs /= (np.linalg.norm(new_dirs, axis=1, keepdims=True)+1e-12)
        losses = RPALosses()  # zeros
        diag = {"dir_mean_z": float(new_dirs[:,2].mean())}
        return new_dirs.astype(np.float32), losses, diag
