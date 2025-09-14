import numpy as np

def summary_stats(arr: np.ndarray) -> dict:
    arr = np.asarray(arr, dtype=np.float64)
    return {
        "min": float(arr.min() if arr.size else 0.0),
        "max": float(arr.max() if arr.size else 0.0),
        "mean": float(arr.mean() if arr.size else 0.0),
        "std": float(arr.std() if arr.size else 0.0),
    }
