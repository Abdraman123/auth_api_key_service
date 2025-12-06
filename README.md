# Auth API - Authentication & API Key Management System

A production-ready FastAPI application implementing JWT authentication and API key management for service-to-service communication.

## Features

✅ **User Authentication (JWT)**
- User signup with email/password
- Login with JWT token generation
- Secure password hashing with bcrypt
- Token-based authentication for protected routes

✅ **API Key Management**
- Create API keys for service-to-service auth
- List and manage your API keys
- Revoke or permanently delete keys
- Optional expiration dates
- Track last usage

✅ **Dual Authentication**
- Endpoints can accept both JWT and API keys
- Flexible authentication middleware
- Support for different auth types per endpoint

✅ **Production Ready**
- PostgreSQL database with Alembic migrations
- Comprehensive error handling
- Input validation with Pydantic
- Repository pattern for database operations
- Service layer for business logic
- Proper project structure

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - ORM with async support
- **PostgreSQL** - Reliable database
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Token-based authentication
- **bcrypt** - Password hashing
- **UV** - Fast Python package manager

## Project Structure

```
auth-api/
├── app/
│   ├── api/
│   │   ├── dependencies.py      # Auth dependencies & middleware
│   │   └── v1/routes/           # API routes
│   ├── db/
│   │   ├── session.py           # Database connection
│   │   └── repositories/        # Data access layer
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   ├── utils/                   # Utilities (security, etc.)
│   ├── config.py                # Configuration
│   └── main.py                  # FastAPI app
├── alembic/                     # Database migrations
├── tests/                       # Test suite
├── .env                         # Environment variables
└── pyproject.toml               # Dependencies
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL
- UV (recommended) or pip

### 2. Installation

```bash
# Clone the repository
git clone <your-repo>
cd auth-api

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb auth_api_db

# Copy environment variables
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://user:password@localhost:5432/auth_api_db
```

### 4. Run Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Run migrations
alembic upgrade head
```

### 5. Start the Server

```bash
# Development mode
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

## API Usage

### 1. User Signup

```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password_123"
  }'
```

### 2. User Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password_123"
  }'

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer"
# }
```

### 3. Get Current User

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGc..."
```

### 4. Create API Key

```bash
curl -X POST "http://localhost:8000/api/v1/keys" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Service",
    "expires_in_days": 90
  }'

# Response includes the API key (save it!):
# {
#   "id": 1,
#   "name": "Production Service",
#   "key": "sk_abc123...",
#   "is_active": true,
#   "expires_at": "2024-04-01T00:00:00Z",
#   "created_at": "2024-01-01T00:00:00Z"
# }
```

### 5. List API Keys

```bash
curl -X GET "http://localhost:8000/api/v1/keys" \
  -H "Authorization: Bearer eyJhbGc..."
```

### 6. Access Protected Resource (JWT)

```bash
curl -X GET "http://localhost:8000/api/v1/protected/resource" \
  -H "Authorization: Bearer eyJhbGc..."
```

### 7. Access Protected Resource (API Key)

```bash
curl -X GET "http://localhost:8000/api/v1/protected/resource" \
  -H "X-API-Key: sk_abc123..."
```

### 8. Revoke API Key

```bash
curl -X DELETE "http://localhost:8000/api/v1/keys/1" \
  -H "Authorization: Bearer eyJhbGc..."
```

## Authentication Methods

### Method 1: JWT Token
Best for user-facing applications, mobile apps, SPAs.

```python
headers = {
    "Authorization": "Bearer <your_jwt_token>"
}
```

### Method 2: API Key
Best for service-to-service communication, scripts, integrations.

```python
headers = {
    "X-API-Key": "<your_api_key>"
}
```

### Method 3: Either (Flexible)
Some endpoints accept both authentication methods.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required (generate securely!) |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 1440 (24 hours) |
| `API_V1_PREFIX` | API route prefix | /api/v1 |
| `ALLOWED_ORIGINS` | CORS origins | http://localhost:3000 |
| `DEBUG` | Debug mode | False |

## Security Best Practices

1. **Never commit `.env` file** - Contains secrets
2. **Use strong SECRET_KEY** - Generate with `openssl rand -hex 32`
3. **Rotate API keys** - Set expiration dates
4. **Use HTTPS in production** - Protect tokens in transit
5. **Validate input** - Pydantic handles this
6. **Rate limiting** - Add in production (e.g., with nginx)
7. **Monitor key usage** - Check `last_used_at` timestamps


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - feel free to use in your projects!

