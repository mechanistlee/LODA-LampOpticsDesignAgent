import numpy as np

def estimate_onf(nodes_dir: np.ndarray) -> np.ndarray:
    # Simple proxy: directions themselves
    return nodes_dir.copy()
