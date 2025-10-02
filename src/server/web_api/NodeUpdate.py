from typing import Optional
from pydantic import BaseModel, Field


class NodeUpdate(BaseModel):
    """Model for updating WaveNode properties via API."""
    endpoint_url: Optional[str] = Field(None, description="New endpoint URL")
    endpoint_id: Optional[str] = Field(None, description="New endpoint ID")
