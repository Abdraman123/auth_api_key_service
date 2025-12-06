from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserSignupRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse
)
from app.schemas.common import MessageResponse
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
def signup(
    request: UserSignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password.
    
    - **email**: Valid email address
    - **password**: Password (minimum 8 characters)
    """
    auth_service = AuthService(db)
    auth_service.signup(email=request.email, password=request.password)
    
    return MessageResponse(message="User created successfully")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login to get access token"
)
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate with email and password to receive a JWT access token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns a JWT token that expires in 24 hours by default.
    """
    auth_service = AuthService(db)
    access_token = auth_service.login(email=request.email, password=request.password)
    
    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info"
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the currently authenticated user.
    
    Requires a valid JWT token in the Authorization header.
    """
    return current_user