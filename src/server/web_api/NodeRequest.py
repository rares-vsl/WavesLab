from typing import Optional
from pydantic import BaseModel, Field

class NodeRequest(BaseModel):
    """Model for HTTP requests sent by active nodes."""
    real_time_consumption: float = Field(..., description="Node's real time consumption")
    username: Optional[str] = Field(None, description="Associated user's username")
