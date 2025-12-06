from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories.user_repository import UserRepository
from app.utils.security import hash_password, verify_password, create_access_token
from app.models.user import User


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
    
    def signup(self, email: str, password: str) -> User:
        """
        Register a new user.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        if self.user_repo.exists_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = hash_password(password)
        user = self.user_repo.create(email=email, hashed_password=hashed_password)
        
        return user
    
    def login(self, email: str, password: str) -> str:
        """
        Authenticate user and return JWT token.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            JWT access token
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = self.user_repo.get_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return access_token
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.user_repo.get_by_id(user_id)