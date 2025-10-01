from enum import Enum

class NodeStatus(str, Enum):
    """Operational status of a WaveNode."""
    OFF = "off"
    ON = "on"