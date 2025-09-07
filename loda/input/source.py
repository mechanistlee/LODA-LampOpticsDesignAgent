"""Source data structures and parsers"""
from dataclasses import dataclass

@dataclass
class ParsedSource:
    position: tuple
    direction: tuple
    angular_distribution: object
    etendue: float
    power: float
