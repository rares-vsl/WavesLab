from pydantic import BaseModel, Field

class VirtualUser(BaseModel):
    """Represents a virtual user in the household simulation."""
    username: str = Field(..., description="Unique name of the virtual user")
