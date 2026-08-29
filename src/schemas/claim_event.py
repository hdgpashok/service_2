import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict


class ClaimEventSchema(BaseModel):
    id: uuid.UUID
    topic: str
    payload: dict[str, Any]
    processing_token: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
