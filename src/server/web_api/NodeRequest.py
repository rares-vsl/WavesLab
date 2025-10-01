from typing import Optional
from pydantic import BaseModel, Field

class NodeRequest(BaseModel):
    """Model for HTTP requests sent by active nodes."""
    node_name: str = Field(..., description="Name of the node sending the request")
    provision_rate: float = Field(..., description="Node's provision rate")
    username: Optional[str] = Field(None, description="Associated user's username")
