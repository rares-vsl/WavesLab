from enum import Enum

class NodeType(str, Enum):
    """Supported utility types for WaveNodes."""
    ELECTRICITY = "electricity"
    WATER = "water"
    GAS = "gas"