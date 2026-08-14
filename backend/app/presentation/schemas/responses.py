from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class StandardResponse(BaseModel):
    status: str = Field(default="success")
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

__all__ = ["StandardResponse"]
