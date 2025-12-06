#!/bin/bash

# Auth API Setup Script
# This script automates the setup process for the Auth API project

set -e  # Exit on error

echo "🚀 Setting up Auth API..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing UV...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
uv venv

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
uv pip install -e ".[dev]"

# Setup environment file
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    
    # Generate a secure secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env with generated secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    fi
    
    echo -e "${GREEN}✓ .env file created with secure SECRET_KEY${NC}"
    echo -e "${YELLOW}⚠️  Please update DATABASE_URL in .env with your PostgreSQL credentials${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Check if PostgreSQL is running
echo -e "${BLUE}Checking PostgreSQL connection...${NC}"
if command -v pg_isready &> /dev/null; then
    if pg_isready > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is running${NC}"
    else
        echo -e "${YELLOW}⚠️  PostgreSQL is not running. Please start PostgreSQL first.${NC}"
        echo "   On macOS: brew services start postgresql"
        echo "   On Linux: sudo systemctl start postgresql"
    fi
else
    echo -e "${YELLOW}⚠️  PostgreSQL client tools not found. Cannot verify connection.${NC}"
fi

# Create database (optional, commented out by default)
echo -e "${BLUE}Would you like to create the database now? (y/n)${NC}"
read -r create_db
if [ "$create_db" = "y" ]; then
    echo "Enter database name (default: auth_api_db):"
    read -r db_name
    db_name=${db_name:-auth_api_db}
    
    if command -v createdb &> /dev/null; then
        createdb "$db_name" 2>/dev/null && echo -e "${GREEN}✓ Database created: $db_name${NC}" || echo -e "${YELLOW}⚠️  Database may already exist${NC}"
    else
        echo -e "${YELLOW}⚠️  createdb command not found. Please create database manually:${NC}"
        echo "   psql -U postgres -c \"CREATE DATABASE $db_name;\""
    fi
fi

# Run migrations
echo -e "${BLUE}Running database migrations...${NC}"
if alembic upgrade head; then
    echo -e "${GREEN}✓ Migrations completed successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Migration failed. Make sure your database is set up correctly.${NC}"
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Update .env with your database credentials if needed"
echo "2. Start the server: uvicorn app.main:app --reload"
echo "3. Visit http://localhost:8000/docs for API documentation"
echo ""
echo -e "${BLUE}Quick commands:${NC}"
echo "  Start server:  uvicorn app.main:app --reload"
echo "  Run tests:     pytest"
echo "  New migration: alembic revision --autogenerate -m 'description'"
echo "  Apply changes: alembic upgrade head"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"