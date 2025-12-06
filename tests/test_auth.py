import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.models.base import Base

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


class TestAuth:
    """Test authentication endpoints."""
    
    def test_signup_success(self, client):
        """Test successful user signup."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "secure_password_123"
            }
        )
        
        assert response.status_code == 201
        assert response.json()["message"] == "User created successfully"
    
    def test_signup_duplicate_email(self, client):
        """Test signup with duplicate email fails."""
        # Create first user
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        # Try to create duplicate
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "different_password"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_signup_weak_password(self, client):
        """Test signup with weak password fails."""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "short"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self, client):
        """Test successful login."""
        # Create user
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "secure_password_123"
            }
        )
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "secure_password_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client):
        """Test login with wrong password fails."""
        # Create user
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "correct_password"
            }
        )
        
        # Try wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_me_success(self, client):
        """Test getting current user info with valid token."""
        # Create and login user
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Get user info
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert data["is_active"] is True
    
    def test_get_me_no_token(self, client):
        """Test getting current user without token fails."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # Forbidden (no auth)
    
    def test_get_me_invalid_token(self, client):
        """Test getting current user with invalid token fails."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401


class TestAPIKeys:
    """Test API key endpoints."""
    
    def get_auth_token(self, client):
        """Helper to create user and get auth token."""
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        return response.json()["access_token"]
    
    def test_create_api_key_success(self, client):
        """Test successful API key creation."""
        token = self.get_auth_token(client)
        
        response = client.post(
            "/api/v1/keys",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Test API Key",
                "expires_in_days": 30
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test API Key"
        assert "key" in data
        assert data["key"].startswith("sk_")
        assert data["is_active"] is True
    
    def test_create_api_key_no_expiration(self, client):
        """Test creating API key without expiration."""
        token = self.get_auth_token(client)
        
        response = client.post(
            "/api/v1/keys",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Permanent Key"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["expires_at"] is None
    
    def test_list_api_keys(self, client):
        """Test listing user's API keys."""
        token = self.get_auth_token(client)
        
        # Create two API keys
        client.post(
            "/api/v1/keys",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Key 1"}
        )
        
        client.post(
            "/api/v1/keys",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Key 2"}
        )
        
        # List keys
        response = client.get(
            "/api/v1/keys",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert "key" not in data[0]  # Actual key not included in list
    
    def test_revoke_api_key(self, client):
        """Test revoking an API key."""
        token = self.get_auth_token(client)
        
        # Create key
        create_response = client.post(
            "/api/v1/keys",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Test Key"}
        )
        
        key_id = create_response.json()["id"]
        
        # Revoke key
        response = client.delete(
            f"/api/v1/keys/{key_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "revoked" in response.json()["message"]
    
    def test_protected_resource_with_api_key(self, client):
        """Test accessing protected resource with API key."""
        token = self.get_auth_token(client)
        
        # Create API key
        create_response = client.post(
            "/api/v1/keys",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Test Key"}
        )
        
        api_key = create_response.json()["key"]
        
        # Access protected resource
        response = client.get(
            "/api/v1/protected/resource",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated_as"] == "api_key"
        assert "key_name" in data