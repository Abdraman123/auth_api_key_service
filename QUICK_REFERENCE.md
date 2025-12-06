# Quick Reference Guide

## 🚀 Getting Started (5 Minutes)

```bash
# 1. Setup (one-time)
chmod +x setup.sh
./setup.sh

# 2. Update .env with your database URL
nano .env

# 3. Start server
uvicorn app.main:app --reload

# 4. Visit docs
# http://localhost:8000/docs
```

## 📋 Common Commands

### Development
```bash
# Start development server
uvicorn app.main:app --reload

# Start with different port
uvicorn app.main:app --reload --port 8080

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black app/

# Lint code
ruff app/
```

### Database
```bash
# Create new migration
alembic revision --autogenerate -m "add new field"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Reset database (careful!)
alembic downgrade base
alembic upgrade head
```

### Package Management
```bash
# Add new dependency
uv pip install package-name
uv pip freeze > requirements.txt

# Update dependencies
uv pip install --upgrade package-name

# Install from requirements
uv pip install -r requirements.txt
```

## 🔑 API Endpoints Cheat Sheet

### Authentication
```bash
# Signup
POST /api/v1/auth/signup
Body: {"email": "user@example.com", "password": "password123"}

# Login
POST /api/v1/auth/login
Body: {"email": "user@example.com", "password": "password123"}
Response: {"access_token": "...", "token_type": "bearer"}

# Get current user
GET /api/v1/auth/me
Header: Authorization: Bearer <token>
```

### API Keys
```bash
# Create API key
POST /api/v1/keys
Header: Authorization: Bearer <token>
Body: {"name": "My Key", "expires_in_days": 30}
Response: {"key": "sk_...", ...}  # Save this key!

# List API keys
GET /api/v1/keys
Header: Authorization: Bearer <token>

# Revoke API key
DELETE /api/v1/keys/{key_id}
Header: Authorization: Bearer <token>

# Permanently delete
DELETE /api/v1/keys/{key_id}/permanent
Header: Authorization: Bearer <token>
```

### Protected Resources
```bash
# With JWT token
GET /api/v1/protected/resource
Header: Authorization: Bearer <token>

# With API key
GET /api/v1/protected/resource
Header: X-API-Key: sk_...

# JWT only endpoint
GET /api/v1/protected/jwt-only
Header: Authorization: Bearer <token>
```

## 💡 Code Examples

### Creating a User and Getting Token
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Signup
response = requests.post(
    f"{BASE_URL}/auth/signup",
    json={
        "email": "test@example.com",
        "password": "secure_password_123"
    }
)
print(response.json())

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "test@example.com",
        "password": "secure_password_123"
    }
)
token = response.json()["access_token"]
print(f"Token: {token}")
```

### Creating and Using API Key
```python
# Create API key (requires JWT)
response = requests.post(
    f"{BASE_URL}/keys",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "name": "Production Service",
        "expires_in_days": 90
    }
)
api_key = response.json()["key"]
print(f"API Key: {api_key}")  # Save this!

# Use API key
response = requests.get(
    f"{BASE_URL}/protected/resource",
    headers={"X-API-Key": api_key}
)
print(response.json())
```

### JavaScript/TypeScript Example
```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// Access protected resource
const response = await fetch(`${BASE_URL}/protected/resource`, {
  headers: {'Authorization': `Bearer ${access_token}`}
});
const data = await response.json();
console.log(data);
```

## 🗂️ Project Structure Quick Reference

```
app/
├── api/
│   ├── dependencies.py     → Auth middleware & dependencies
│   └── v1/routes/
│       ├── auth.py         → Signup, login, get current user
│       ├── api_keys.py     → Create, list, revoke keys
│       └── protected.py    → Example protected endpoints
├── db/
│   ├── session.py          → Database connection & session
│   └── repositories/       → Database operations (CRUD)
├── models/                 → SQLAlchemy models (User, APIKey)
├── schemas/                → Pydantic request/response models
├── services/               → Business logic layer
├── utils/
│   └── security.py         → JWT, password hashing, key generation
├── config.py               → Environment variables & settings
└── main.py                 → FastAPI app & startup
```

## 🔐 Security Checklist

- [ ] Use strong SECRET_KEY (generate with `openssl rand -hex 32`)
- [ ] Never commit `.env` file
- [ ] Use HTTPS in production
- [ ] Set reasonable token expiration (default: 24h)
- [ ] Add rate limiting in production
- [ ] Monitor API key usage
- [ ] Rotate keys periodically
- [ ] Use different keys for different environments
- [ ] Implement proper CORS settings
- [ ] Log authentication failures

## 🐛 Troubleshooting

### "Connection refused" error
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### "Database does not exist"
```bash
createdb auth_api_db
```

### "Alembic migration failed"
```bash
# Check current revision
alembic current

# Try manual migration
alembic upgrade head --sql  # Preview SQL
alembic upgrade head        # Apply
```

### "Import errors"
```bash
# Reinstall in editable mode
uv pip install -e .

# Check Python path
echo $PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### "Token validation failed"
- Verify SECRET_KEY hasn't changed
- Check token hasn't expired
- Ensure proper header format: `Authorization: Bearer <token>`

## 📊 Testing Tips

```bash
# Run specific test
pytest tests/test_auth.py::TestAuth::test_login_success -v

# Run with print output
pytest -s

# Stop on first failure
pytest -x

# Run in parallel (install pytest-xdist)
pytest -n auto
```

## 🚀 Production Deployment Tips

1. **Environment Variables**
   - Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
   - Never use DEBUG=True in production
   - Set proper ALLOWED_ORIGINS

2. **Database**
   - Use connection pooling
   - Set up database backups
   - Monitor query performance

3. **Security**
   - Enable HTTPS
   - Add rate limiting (nginx, CloudFlare)
   - Implement request logging
   - Set up monitoring/alerting

4. **Performance**
   - Use Redis for caching
   - Add database indexes
   - Enable gzip compression
   - Use CDN for static files

## 📚 Additional Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Alembic Docs: https://alembic.sqlalchemy.org
- JWT.io: https://jwt.io
- OWASP Auth Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html