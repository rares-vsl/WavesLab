import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from core.model.Endpoint import Endpoint
from core.model.NodeStatus import NodeStatus
from core.model.NodeType import NodeType


class WaveNode(BaseModel):
    """Model representing a WaveNode - a smart furniture connection."""
    id: str = Field(..., description="Slugified version of the name")
    name: str = Field(..., description="Unique human-readable identifier")
    node_type: NodeType = Field(..., description="Type of utility delivered")
    endpoint: Endpoint = Field(None, description="Destination URL for data transmission")
    status: NodeStatus = Field(default=NodeStatus.OFF, description="Whether the node is active")
    provision_rate: float = Field(..., ge=0, description="Amount of utility delivered")
    assigned_user: Optional[str] = Field(None, description="Username of associated user")

    @field_validator('id', mode='before')
    @classmethod
    def generate_id_from_name(cls, v, info):
        """Generate slugified ID from name if not provided."""
        if v is None and 'name' in info.data:
            # Slugify the name: lowercase, replace spaces/special chars with hyphens
            return re.sub(r'[^a-z0-9]+', '-', info.data['name'].lower()).strip('-')
        return v
