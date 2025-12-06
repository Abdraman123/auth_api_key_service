from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class APIKeyCreateRequest(BaseModel):
    """Request model for creating an API key."""
    name: str = Field(..., min_length=1, max_length=255)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """Response model for API key (includes the actual key only on creation)."""
    id: int
    name: str
    key: Optional[str] = None  # Only returned on creation
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyListItem(BaseModel):
    """Response model for API key in list (without the actual key)."""
    id: int
    name: str
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True