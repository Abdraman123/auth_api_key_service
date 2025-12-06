from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User


class UserRepository:
    """Repository for User database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, email: str, hashed_password: str) -> User:
        """Create a new user."""
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.get(User, user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        stmt = select(User.id).where(User.email == email)
        result = self.db.execute(stmt)
        return result.first() is not None
    
    def update(self, user: User) -> User:
        """Update user."""
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """Delete user."""
        self.db.delete(user)
        self.db.commit()