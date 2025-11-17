#!/usr/bin/env pwsh
# Clear all Kafka topics (reset event streams)

Write-Host "🗑️  Clearing Kafka topics..." -ForegroundColor Yellow
Write-Host ""

$topics = @(
    "network_data",
    "anomalies",
    "attack_classified",
    "attack_predicted",
    "alerts",
    "fl_events"
)

foreach ($topic in $topics) {
    Write-Host "Deleting topic: $topic" -ForegroundColor Cyan
    docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic $topic 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Deleted $topic" -ForegroundColor Green
    } else {
        Write-Host "⚠ Topic $topic may not exist or already deleted" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "✅ Kafka topics cleared!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Topics will be auto-created when services start producing messages." -ForegroundColor Cyan
Write-Host ""
