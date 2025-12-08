from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.api_key_service import APIKeyService
from app.utils.security import decode_access_token
from app.models.user import User
from app.models.api_key import APIKey

# Security scheme for JWT
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
        
    Returns:
        Authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from token
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


def get_api_key_auth(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    Dependency to authenticate using API key.
    
    Args:
        x_api_key: API key from header
        db: Database session
        
    Returns:
        Validated API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    api_key_service = APIKeyService(db)
    api_key = api_key_service.validate_api_key(x_api_key)
    
    return api_key


def get_current_user_or_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> tuple[Optional[User], Optional[APIKey]]:
    """
    Dependency that allows either JWT token or API key authentication.
    
    Args:
        credentials: HTTP Bearer token (optional)
        x_api_key: API key from header (optional)
        db: Database session
        
    Returns:
        Tuple of (user, api_key) where one will be None
        
    Raises:
        HTTPException: If neither authentication method is valid
    """
    # Try API key first
    if x_api_key:
        try:
            api_key_service = APIKeyService(db)
            api_key = api_key_service.validate_api_key(x_api_key)
            return (None, api_key)
        except HTTPException:
            pass
    
    # Try JWT second
    if credentials:
        try:
            user = get_current_user(credentials, db)
            return (user, None)
        except HTTPException:
            pass
    
    # Neither worked
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid authentication required (JWT token or API key)"
    )