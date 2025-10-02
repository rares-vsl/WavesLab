from pydantic import BaseModel, Field

class Endpoint(BaseModel):
    """Represents an endpoint with a URL and the ID to transmit."""
    url: str = Field(..., description="URL of the endpoint")
    ID: str = Field(..., description="ID of the node in the destination server")
