from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.api_key import APIKey


class APIKeyRepository:
    """Repository for APIKey database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        key: str,
        name: str,
        user_id: int,
        expires_in_days: Optional[int] = None
    ) -> APIKey:
        """Create a new API key."""
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        api_key = APIKey(
            key=key,
            name=name,
            user_id=user_id,
            expires_at=expires_at
        )
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        return api_key
    
    def get_by_id(self, key_id: int) -> Optional[APIKey]:
        """Get API key by ID."""
        return self.db.get(APIKey, key_id)
    
    def get_by_key(self, key: str) -> Optional[APIKey]:
        """Get API key by key string."""
        stmt = select(APIKey).where(APIKey.key == key)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_all_by_user(self, user_id: int) -> List[APIKey]:
        """Get all API keys for a user."""
        stmt = select(APIKey).where(APIKey.user_id == user_id).order_by(APIKey.created_at.desc())
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def update_last_used(self, api_key: APIKey) -> APIKey:
        """Update the last_used_at timestamp."""
        api_key.last_used_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(api_key)
        return api_key
    
    def revoke(self, api_key: APIKey) -> APIKey:
        """Revoke (deactivate) an API key."""
        api_key.is_active = False
        self.db.commit()
        self.db.refresh(api_key)
        return api_key
    
    def delete(self, api_key: APIKey) -> None:
        """Delete an API key."""
        self.db.delete(api_key)
        self.db.commit()