# FedICS Utility Scripts

This directory contains utility scripts for development, testing, and operations.

## Available Scripts

### 🚀 `setup_dev.ps1` - Development Environment Setup

One-command setup for FedICS development environment.

**What it does:**
- ✓ Checks prerequisites (Docker, Python)
- ✓ Creates `.env` file from template
- ✓ Sets up Python virtual environment
- ✓ Installs dependencies
- ✓ Builds Docker images
- ✓ Starts infrastructure services
- ✓ Runs database migrations
- ✓ Seeds database with sample data

**Usage:**
```powershell
.\scripts\setup_dev.ps1
```

**Prerequisites:**
- Docker Desktop installed and running
- Python 3.10+ installed
- PowerShell 5.1+ (Windows) or PowerShell Core 7+ (cross-platform)

---

### 🗑️ `clear_kafka.ps1` - Reset Kafka Topics

Deletes all Kafka topics to reset event streams.

**What it does:**
- Deletes all 6 FedICS topics:
  - `network_data`
  - `anomalies`
  - `attack_classified`
  - `attack_predicted`
  - `alerts`
  - `fl_events`

**Usage:**
```powershell
.\scripts\clear_kafka.ps1
```

**Note:** Topics will be auto-created when services start producing messages.

---

### 🌱 `seed_db.py` - Populate Database with Sample Data

Seeds the PostgreSQL database with realistic test data.

**What it creates:**
- 50 network packets (various protocols: TCP, UDP, Modbus/TCP, DNP3)
- 20 alerts with detection sources and MITRE ATT&CK mappings
- 5 federated learning rounds with client participation records
- 12 attack predictions with technique forecasts

**Usage:**
```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Run seeding script
python scripts\seed_db.py
```

**Prerequisites:**
- PostgreSQL running (via Docker Compose)
- Backend dependencies installed: `cd services/backend && poetry install`
- Database migrations applied: `cd services/backend && poetry run alembic upgrade head`

---

### 🧪 `run_integration_tests.ps1` - Integration Test Suite

Validates the entire FedICS infrastructure.

**What it tests:**
1. ✓ Kafka connectivity and topics
2. ✓ PostgreSQL connectivity
3. ✓ Redis connectivity
4. ✓ Neo4j connectivity
5. ✓ Backend API health
6. ✓ Dashboard accessibility
7. ✓ Flower server status
8. ✓ Python unit tests (if tests exist)

**Usage:**
```powershell
.\scripts\run_integration_tests.ps1
```

**Use cases:**
- Pre-deployment validation
- CI/CD pipeline checks
- Troubleshooting service connectivity

---

## Quick Start Workflow

For a fresh setup, run scripts in this order:

```powershell
# 1. Setup development environment
.\scripts\setup_dev.ps1

# 2. Verify everything works
.\scripts\run_integration_tests.ps1

# 3. Start development
make dev
```

## Maintenance Workflows

**Reset Kafka streams:**
```powershell
.\scripts\clear_kafka.ps1
docker compose restart network-simulator
```

**Reset database:**
```powershell
docker compose down postgres
docker volume rm flower-set-up_pgdata
docker compose up -d postgres
# Wait 5 seconds
cd services/backend
poetry run alembic upgrade head
poetry run python ../../scripts/seed_db.py
```

**Full reset (nuclear option):**
```powershell
docker compose down -v
.\scripts\setup_dev.ps1
```

---

## Adding New Scripts

When adding new utility scripts:

1. Use `.ps1` extension for PowerShell scripts
2. Use `.py` extension for Python scripts
3. Use `.sh` extension for Bash scripts (Linux/macOS)
4. Add shebang line: `#!/usr/bin/env pwsh` or `#!/usr/bin/env python3`
5. Document in this README
6. Update `Makefile` if appropriate

**Script template:**
```powershell
#!/usr/bin/env pwsh
# Script: My New Script
# Purpose: What this script does

Write-Host "🚀 My New Script" -ForegroundColor Cyan
# ... your code here
```

---

## Troubleshooting

**"Script cannot be loaded because running scripts is disabled"**
```powershell
# Enable script execution (run PowerShell as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"Docker command not found"**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop

**"Python command not found"**
- Install Python 3.10+: https://www.python.org/downloads/
- Make sure Python is in your PATH

**"Permission denied" on Linux/macOS**
```bash
# Make scripts executable
chmod +x scripts/*.sh scripts/*.ps1
```

---

## See Also

- [Makefile](../Makefile) - Pre-configured commands using these scripts
- [Development Guide](../docs/DEVELOPMENT.md) - Local development setup
- [Project Overview](../docs/PROJECT_OVERVIEW.md) - System architecture
