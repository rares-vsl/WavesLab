from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer


class NodeRequest(BaseModel):
    """Model for HTTP requests sent by active nodes."""
    realTimeConsumption: float = Field(..., description="Node's real time consumption")
    username: Optional[str] = Field(None, description="Associated user's username")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(), description="Timestamp of the measurement")

    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
