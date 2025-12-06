from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.api_key_service import APIKeyService
from app.schemas.api_key import (
    APIKeyCreateRequest,
    APIKeyResponse,
    APIKeyListItem
)
from app.schemas.common import MessageResponse
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/keys", tags=["API Keys"])


@router.post(
    "",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new API key"
)
def create_api_key(
    request: APIKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key for the authenticated user.
    
    - **name**: Descriptive name for the API key (e.g., "Production Server")
    - **expires_in_days**: Optional expiration period in days (1-365)
    
    ⚠️ **IMPORTANT**: The actual API key is only returned once during creation.
    Save it securely - you won't be able to retrieve it again!
    """
    api_key_service = APIKeyService(db)
    api_key = api_key_service.create_api_key(
        name=request.name,
        user_id=current_user.id,
        expires_in_days=request.expires_in_days
    )
    
    return api_key


@router.get(
    "",
    response_model=List[APIKeyListItem],
    summary="List all your API keys"
)
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a list of all API keys belonging to the authenticated user.
    
    Note: The actual key strings are not included in this response for security.
    """
    api_key_service = APIKeyService(db)
    api_keys = api_key_service.get_user_api_keys(current_user.id)
    
    return api_keys


@router.delete(
    "/{key_id}",
    response_model=MessageResponse,
    summary="Revoke an API key"
)
def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke (deactivate) an API key.
    
    The key will no longer work for authentication but will remain in the database.
    
    - **key_id**: ID of the API key to revoke
    """
    api_key_service = APIKeyService(db)
    api_key_service.revoke_api_key(key_id=key_id, user_id=current_user.id)
    
    return MessageResponse(message="API key revoked successfully")


@router.delete(
    "/{key_id}/permanent",
    response_model=MessageResponse,
    summary="Permanently delete an API key"
)
def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete an API key from the database.
    
    This action cannot be undone.
    
    - **key_id**: ID of the API key to delete
    """
    api_key_service = APIKeyService(db)
    api_key_service.delete_api_key(key_id=key_id, user_id=current_user.id)
    
    return MessageResponse(message="API key deleted successfully")