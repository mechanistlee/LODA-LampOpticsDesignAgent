import numpy as np

def loss_candela(pred: np.ndarray, target: np.ndarray, legal_mask: np.ndarray) -> float:
    mask = legal_mask.astype(bool)
    if pred.size == 0 or target.size == 0:
        return 0.0
    d = (pred[mask] - target[mask])
    return float(np.mean(d*d))

def loss_illuminance(illu_map: np.ndarray) -> float:
    return float(np.var(illu_map))

def loss_efficiency(efficiency: float) -> float:
    return float(-efficiency)
