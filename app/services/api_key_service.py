from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories.api_key_repository import APIKeyRepository
from app.utils.security import generate_api_key
from app.models.api_key import APIKey


class APIKeyService:
    """Service for API key operations."""
    
    def __init__(self, db: Session):
        self.api_key_repo = APIKeyRepository(db)
    
    def create_api_key(
        self,
        name: str,
        user_id: int,
        expires_in_days: Optional[int] = None
    ) -> APIKey:
        """
        Create a new API key for a user.
        
        Args:
            name: Name/description of the API key
            user_id: Owner user ID
            expires_in_days: Optional expiration in days
            
        Returns:
            Created API key with the key string
        """
        # Generate unique API key
        key = generate_api_key()
        
        # Create API key in database
        api_key = self.api_key_repo.create(
            key=key,
            name=name,
            user_id=user_id,
            expires_in_days=expires_in_days
        )
        
        return api_key
    
    def get_user_api_keys(self, user_id: int) -> List[APIKey]:
        """
        Get all API keys for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of API keys
        """
        return self.api_key_repo.get_all_by_user(user_id)
    
    def validate_api_key(self, key: str) -> APIKey:
        """
        Validate an API key and return it if valid.
        
        Args:
            key: API key string
            
        Returns:
            Valid API key
            
        Raises:
            HTTPException: If key is invalid, inactive, or expired
        """
        api_key = self.api_key_repo.get_by_key(key)
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        if not api_key.is_valid:
            if api_key.is_expired:
                detail = "API key has expired"
            else:
                detail = "API key is inactive"
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detail
            )
        
        # Update last used timestamp
        self.api_key_repo.update_last_used(api_key)
        
        return api_key
    
    def revoke_api_key(self, key_id: int, user_id: int) -> APIKey:
        """
        Revoke (deactivate) an API key.
        
        Args:
            key_id: API key ID
            user_id: User ID (for authorization)
            
        Returns:
            Revoked API key
            
        Raises:
            HTTPException: If key not found or unauthorized
        """
        api_key = self.api_key_repo.get_by_id(key_id)
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        # Check ownership
        if api_key.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to revoke this API key"
            )
        
        # Revoke the key
        return self.api_key_repo.revoke(api_key)
    
    def delete_api_key(self, key_id: int, user_id: int) -> None:
        """
        Permanently delete an API key.
        
        Args:
            key_id: API key ID
            user_id: User ID (for authorization)
            
        Raises:
            HTTPException: If key not found or unauthorized
        """
        api_key = self.api_key_repo.get_by_id(key_id)
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        # Check ownership
        if api_key.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this API key"
            )
        
        # Delete the key
        self.api_key_repo.delete(api_key)