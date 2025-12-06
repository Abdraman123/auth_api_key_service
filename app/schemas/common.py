from pydantic import BaseModel
from typing import Optional


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class ErrorResponse(BaseModel):
    """Generic error response."""
    detail: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str