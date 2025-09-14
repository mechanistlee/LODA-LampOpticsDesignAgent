from dataclasses import dataclass
import numpy as np

@dataclass
class BRM:
    indices: np.ndarray  # (K,2): (i_lpf, j_bin)
    weights: np.ndarray  # (K,)

class BRMComputer:
    def compute(self, n_lpf: int, n_bins: int) -> BRM:
        # Stub: map each LPF index to bin 0 with weight 1
        idx = np.stack([np.arange(n_lpf, dtype=int), np.zeros(n_lpf, dtype=int)], axis=1)
        w = np.ones((n_lpf,), dtype=np.float32)
        return BRM(idx, w)
