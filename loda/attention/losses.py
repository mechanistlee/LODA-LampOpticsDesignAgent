from dataclasses import dataclass

@dataclass
class RPALosses:
    L_occlusion: float = 0.0
    L_normal: float = 0.0
    L_arrival: float = 0.0
    L_space: float = 0.0
    L_energy: float = 0.0
    @property
    def total(self) -> float:
        return self.L_occlusion + self.L_normal + self.L_arrival + self.L_space + self.L_energy
