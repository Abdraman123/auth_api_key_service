from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_current_user_or_api_key
from app.db.session import get_db
from app.api.dependencies import get_current_user_or_api_key
from app.models.user import User
from app.models.api_key import APIKey

router = APIRouter(prefix="/protected", tags=["Protected Resources"])


@router.get(
    "/resource",
    summary="Access a protected resource"
)
def get_protected_resource(
    auth: tuple[Optional[User], Optional[APIKey]] = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db)
):
    """
    Example protected endpoint that accepts both JWT and API key authentication.
    
    **Authentication Options:**
    - Option 1: JWT Token - Use `Authorization: Bearer <token>` header
    - Option 2: API Key - Use `X-API-Key: <key>` header
    
    This demonstrates how you can create endpoints that accept multiple authentication methods.
    """
    user, api_key = auth
    
    if user:
        return {
            "message": "Access granted via JWT",
            "authenticated_as": "user",
            "user_id": user.id,
            "email": user.email
        }
    elif api_key:
        return {
            "message": "Access granted via API Key",
            "authenticated_as": "api_key",
            "key_name": api_key.name,
            "key_id": api_key.id,
            "owner_user_id": api_key.user_id
        }
    
    # This shouldn't happen due to dependency validation
    return {"message": "Authentication failed"}


@router.get(
    "/jwt-only",
    summary="JWT-only protected resource"
)
def get_jwt_only_resource(
    current_user: User = Depends(get_current_user)
):
    """
    Example endpoint that only accepts JWT authentication.
    
    Use `Authorization: Bearer <token>` header.
    """
    return {
        "message": "This endpoint only accepts JWT tokens",
        "user_id": current_user.id,
        "email": current_user.email
    }