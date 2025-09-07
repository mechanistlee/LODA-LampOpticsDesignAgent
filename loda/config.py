"""Configuration dataclasses for LODA inputs"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple

@dataclass
class SourceInfo:
    position: Tuple[float, float, float]
    direction: Tuple[float, float, float]
    angular_distribution: Optional[Any] = None  # placeholder for S(theta,phi)
    etendue: Optional[float] = None
    power: Optional[float] = None

@dataclass
class SpaceInfo:
    bounds: Any  # placeholder for allowed structure volume

@dataclass
class OutputSurfaceInfo:
    mesh: Optional[Any] = None  # placeholder for 3D mesh (trimesh)
    lens_structure: Optional[Dict[str, Any]] = field(default_factory=dict)

@dataclass
class LightingCode:
    candela_map: Optional[Any] = None

@dataclass
class OpticsConstraints:
    min_radius: Optional[float] = None
    max_size: Optional[Tuple[float, float, float]] = None
    reflectance: Optional[float] = None
    gradient_limit: Optional[float] = None

@dataclass
class LODAConfig:
    source: SourceInfo
    space: SpaceInfo
    output_surface: OutputSurfaceInfo
    lighting_code: Optional[LightingCode] = None
    constraints: Optional[OpticsConstraints] = None
    misc: Dict[str, Any] = field(default_factory=dict)
