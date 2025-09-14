"""BSDF 스켈레톤: dielectric, mirror, ggx, absorb.
샘플/평가 함수 자리에 placeholder.
"""
from typing import Dict, Any

class BSDF:
    def __init__(self, mat_type: str, params: Dict[str, Any]):
        self.type = mat_type
        self.params = params

    def sample(self, normal, wi, rng) -> Dict[str, Any]:  # placeholder
        return {"wo": wi, "throughput": 1.0}

    def evaluate(self, normal, wi, wo) -> float:  # placeholder
        return 1.0


def make_bsdf(mat_type: str, params: Dict[str, Any]) -> BSDF:
    return BSDF(mat_type, params)
