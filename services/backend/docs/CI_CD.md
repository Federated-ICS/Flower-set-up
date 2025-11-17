# CI/CD Documentation

## Overview

This project uses GitHub Actions for continuous integration and continuous deployment. The CI/CD pipeline ensures code quality, runs tests, and performs security checks on every commit.

## Workflows

### 1. CI Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

#### Test Job
- Sets up Python 3.11
- Installs Poetry and dependencies
- Starts PostgreSQL service container
- Runs database migrations
- Executes full test suite with coverage
- Uploads coverage to Codecov

**Services:**
- PostgreSQL 15 (test database)

**Environment Variables:**
```bash
DATABASE_URL=postgresql+asyncpg://ics_user:ics_password@localhost:5432/ics_threat_detection_test
```

#### Lint Job
- Checks code formatting with Black
- Verifies import sorting with isort
- Runs flake8 linting

**Configuration:**
- Max line length: 100
- Ignores: E203, W503 (Black compatibility)

#### Type Check Job
- Runs mypy static type checking
- Ignores missing imports for third-party libraries

### 2. Quick Check (`quick-check.yml`)

**Purpose:** Fast feedback for API tests

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**What it does:**
- Runs only API tests (`tests/test_api/`)
- Faster than full CI pipeline
- Good for quick validation

### 3. Security Scan (`security.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Weekly schedule (Monday 00:00 UTC)

**Scans:**
- **Safety**: Checks for known security vulnerabilities in dependencies
- **Bandit**: Static security analysis for Python code

**Artifacts:**
- Bandit security report (JSON format)

## Local CI Simulation

Run the same checks locally before pushing:

### Full Test Suite
```bash
# Run all tests with coverage
poetry run pytest tests/ -v --cov=app --cov-report=xml --cov-report=term

# Run only API tests
poetry run pytest tests/test_api/ -v

# Run with specific markers
poetry run pytest -m "not slow" -v
```

### Code Quality Checks
```bash
# Format code (auto-fix)
poetry run black app/ tests/
poetry run isort app/ tests/

# Check formatting (no changes)
poetry run black --check app/ tests/
poetry run isort --check-only app/ tests/

# Lint
poetry run flake8 app/ tests/ --max-line-length=100 --extend-ignore=E203,W503
```

### Type Checking
```bash
poetry run mypy app/ --ignore-missing-imports
```

### Security Scanning
```bash
# Install security tools
pip install bandit safety

# Run Bandit
bandit -r app/ -f json -o bandit-report.json

# Run Safety (requires API key or use free tier)
poetry export -f requirements.txt --output requirements.txt --without-hashes
safety check --file=requirements.txt
```

## CI Configuration Files

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

addopts = 
    --strict-markers
    --tb=short
    --disable-warnings

markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
```

### pyproject.toml (relevant sections)
```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
```

## GitHub Secrets

Required secrets for full CI functionality:

### Optional Secrets
- `SAFETY_API_KEY` - For Safety dependency scanning (free tier available)
- `CODECOV_TOKEN` - For private repositories (public repos don't need this)

### Setting Secrets
1. Go to repository Settings
2. Navigate to Secrets and variables → Actions
3. Click "New repository secret"
4. Add the secret name and value

## Status Badges

Add these badges to your README (replace `YOUR_USERNAME` and `YOUR_REPO`):

```markdown
[![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml)
[![Quick Check](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/quick-check.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/quick-check.yml)
[![Security Scan](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/security.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO)
```

## Troubleshooting

### Tests Fail in CI but Pass Locally

**Possible causes:**
1. Database connection issues
2. Missing environment variables
3. Different Python versions
4. Cached dependencies

**Solutions:**
```bash
# Use same Python version as CI
pyenv install 3.11
pyenv local 3.11

# Clear Poetry cache
poetry cache clear pypi --all
poetry install --no-cache

# Use test database URL
export DATABASE_URL=postgresql+asyncpg://ics_user:ics_password@localhost:5432/ics_threat_detection_test
```

### PostgreSQL Service Not Ready

The workflow includes health checks, but if issues persist:

```yaml
- name: Wait for PostgreSQL
  run: |
    until pg_isready -h localhost -p 5432 -U ics_user; do
      echo "Waiting for PostgreSQL..."
      sleep 2
    done
```

### Coverage Upload Fails

Codecov upload is set to `fail_ci_if_error: false`, so it won't block CI. To debug:

1. Check Codecov token is set (for private repos)
2. Verify coverage.xml is generated
3. Check Codecov service status

### Dependency Cache Issues

Clear the cache by:
1. Go to Actions tab
2. Click "Caches" in the left sidebar
3. Delete relevant caches
4. Re-run the workflow

## Best Practices

### Before Committing
```bash
# Run quick checks
poetry run black app/ tests/
poetry run isort app/ tests/
poetry run pytest tests/test_api/ -v
```

### Before Creating PR
```bash
# Run full CI locally
poetry run pytest tests/ -v --cov=app
poetry run black --check app/ tests/
poetry run isort --check-only app/ tests/
poetry run flake8 app/ tests/ --max-line-length=100
poetry run mypy app/ --ignore-missing-imports
```

### Writing Tests
- Add tests for all new features
- Maintain test coverage above 80%
- Use appropriate markers (`@pytest.mark.api`, etc.)
- Keep tests fast (mock external services)

### Code Quality
- Follow Black formatting
- Sort imports with isort
- Add type hints where possible
- Write docstrings for public functions

## Monitoring

### GitHub Actions Dashboard
- View workflow runs: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
- Check individual job logs
- Download artifacts (test reports, coverage)

### Codecov Dashboard
- View coverage trends: `https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO`
- Check coverage by file
- See coverage changes in PRs

## Future Enhancements

Planned CI/CD improvements:

- [ ] Automated deployment to staging
- [ ] Performance testing
- [ ] Integration tests with real services
- [ ] Docker image building and publishing
- [ ] Automated changelog generation
- [ ] Release automation
- [ ] E2E testing with frontend

---

**Last Updated:** November 11, 2025
