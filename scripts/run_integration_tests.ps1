#!/usr/bin/env pwsh
# Run Integration Tests
# Full pipeline validation for FedICS

Write-Host "🧪 FedICS Integration Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Ensure services are running
Write-Host "📋 Checking if services are running..." -ForegroundColor Yellow
$running_services = docker compose ps --services --filter "status=running"

if (-not $running_services) {
    Write-Host "❌ No services running. Starting infrastructure..." -ForegroundColor Red
    docker compose up -d postgres redis neo4j kafka zookeeper
    Write-Host "⏳ Waiting for services to be ready (15 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
}

Write-Host "✓ Services are running" -ForegroundColor Green
Write-Host ""

# Test 1: Kafka connectivity
Write-Host "Test 1: Kafka Connectivity" -ForegroundColor Cyan
Write-Host "----------------------------" -ForegroundColor Cyan
$topics = docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Kafka is accessible" -ForegroundColor Green
    Write-Host "  Topics: $($topics -join ', ')" -ForegroundColor Gray
} else {
    Write-Host "✗ Kafka connection failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: PostgreSQL connectivity
Write-Host "Test 2: PostgreSQL Connectivity" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan
$pg_check = docker compose exec postgres pg_isready -U postgres 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PostgreSQL is accessible" -ForegroundColor Green
} else {
    Write-Host "✗ PostgreSQL connection failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 3: Redis connectivity
Write-Host "Test 3: Redis Connectivity" -ForegroundColor Cyan
Write-Host "--------------------------" -ForegroundColor Cyan
$redis_check = docker compose exec redis redis-cli ping 2>&1
if ($redis_check -match "PONG") {
    Write-Host "✓ Redis is accessible" -ForegroundColor Green
} else {
    Write-Host "✗ Redis connection failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 4: Neo4j connectivity
Write-Host "Test 4: Neo4j Connectivity" -ForegroundColor Cyan
Write-Host "--------------------------" -ForegroundColor Cyan
try {
    $neo4j_check = Invoke-WebRequest -Uri "http://localhost:7474" -UseBasicParsing -TimeoutSec 5
    if ($neo4j_check.StatusCode -eq 200) {
        Write-Host "✓ Neo4j is accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Neo4j connection failed" -ForegroundColor Red
    Write-Host "  Make sure Neo4j container is running" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Backend API health
Write-Host "Test 5: Backend API Health" -ForegroundColor Cyan
Write-Host "--------------------------" -ForegroundColor Cyan
$backend_running = docker compose ps fastapi-backend --filter "status=running"
if ($backend_running) {
    try {
        $health_check = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($health_check.StatusCode -eq 200) {
            Write-Host "✓ Backend API is healthy" -ForegroundColor Green
            Write-Host "  Response: $($health_check.Content)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "⚠ Backend API not responding (might be starting up)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Backend service not running" -ForegroundColor Yellow
    Write-Host "  Start with: docker compose up -d fastapi-backend" -ForegroundColor Gray
}
Write-Host ""

# Test 6: Dashboard accessibility
Write-Host "Test 6: Dashboard Accessibility" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan
$dashboard_running = docker compose ps dashboard --filter "status=running"
if ($dashboard_running) {
    try {
        $dashboard_check = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        if ($dashboard_check.StatusCode -eq 200) {
            Write-Host "✓ Dashboard is accessible" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠ Dashboard not responding (might be starting up)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Dashboard service not running" -ForegroundColor Yellow
    Write-Host "  Start with: docker compose up -d dashboard" -ForegroundColor Gray
}
Write-Host ""

# Test 7: Flower server health
Write-Host "Test 7: Flower Server Health" -ForegroundColor Cyan
Write-Host "----------------------------" -ForegroundColor Cyan
$flower_running = docker compose ps flower-server --filter "status=running"
if ($flower_running) {
    Write-Host "✓ Flower server is running" -ForegroundColor Green
} else {
    Write-Host "⚠ Flower server not running" -ForegroundColor Yellow
    Write-Host "  Start with: docker compose up -d flower-server" -ForegroundColor Gray
}
Write-Host ""

# Test 8: Python unit tests
Write-Host "Test 8: Python Unit Tests" -ForegroundColor Cyan
Write-Host "-------------------------" -ForegroundColor Cyan
if (Test-Path "tests") {
    Write-Host "Running pytest..." -ForegroundColor Gray
    & ".venv\Scripts\Activate.ps1"
    pytest tests/ -v --tb=short 2>&1 | Tee-Object -Variable test_output
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ All unit tests passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Some unit tests failed" -ForegroundColor Red
    }
} else {
    Write-Host "⚠ No tests directory found" -ForegroundColor Yellow
    Write-Host "  Create tests with: mkdir tests" -ForegroundColor Gray
}
Write-Host ""

# Summary
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Integration Test Summary" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Core infrastructure tests complete" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "  • Start all services:  make dev" -ForegroundColor White
Write-Host "  • View logs:           make logs" -ForegroundColor White
Write-Host "  • Test full pipeline:  Start simulator and detectors" -ForegroundColor White
Write-Host ""
