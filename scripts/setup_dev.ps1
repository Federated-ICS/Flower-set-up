#!/usr/bin/env pwsh
# FedICS Development Environment Setup Script
# One-command setup for Windows (PowerShell)

Write-Host "🚀 FedICS Development Environment Setup" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "✓ Docker found" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Python
try {
    python --version | Out-Null
    Write-Host "✓ Python found" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.10+." -ForegroundColor Red
    exit 1
}

# Check if .env exists
Write-Host ""
Write-Host "📝 Setting up configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
    Write-Host "⚠️  Please review and update .env with your settings" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Create Python virtual environment
Write-Host ""
Write-Host "🐍 Setting up Python environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "✓ Created virtual environment" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host ""
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Build Docker images
Write-Host ""
Write-Host "🐳 Building Docker images..." -ForegroundColor Yellow
docker compose build
Write-Host "✓ Docker images built" -ForegroundColor Green

# Start infrastructure services
Write-Host ""
Write-Host "🚀 Starting infrastructure services..." -ForegroundColor Yellow
docker compose up -d postgres redis neo4j kafka zookeeper
Write-Host "✓ Infrastructure services started" -ForegroundColor Green

# Wait for services to be ready
Write-Host ""
Write-Host "⏳ Waiting for services to be ready (15 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Run database migrations
Write-Host ""
Write-Host "🗄️  Running database migrations..." -ForegroundColor Yellow
Push-Location services/backend
poetry install
poetry run alembic upgrade head
Pop-Location
Write-Host "✓ Database migrations complete" -ForegroundColor Green

# Seed database
Write-Host ""
Write-Host "🌱 Seeding database with sample data..." -ForegroundColor Yellow
Push-Location services/backend
poetry run python scripts/seed_database.py
Pop-Location
Write-Host "✓ Database seeded" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Quick Start:" -ForegroundColor Cyan
Write-Host "  • Start all services:     make dev" -ForegroundColor White
Write-Host "  • View logs:              make logs" -ForegroundColor White
Write-Host "  • Run tests:              make test" -ForegroundColor White
Write-Host "  • Access dashboard:       http://localhost:3000" -ForegroundColor White
Write-Host "  • Access API docs:        http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • Access Neo4j browser:   http://localhost:7474" -ForegroundColor White
Write-Host ""
Write-Host "📖 Run 'make help' for more commands" -ForegroundColor Cyan
Write-Host ""
