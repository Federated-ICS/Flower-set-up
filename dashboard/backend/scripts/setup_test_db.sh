#!/bin/bash

echo "🧪 Setting up test database..."

# Create test database
docker exec ics-postgres psql -U ics_user -d postgres -c "DROP DATABASE IF EXISTS ics_threat_detection_test;" 2>/dev/null || true
docker exec ics-postgres psql -U ics_user -d postgres -c "CREATE DATABASE ics_threat_detection_test;"

echo "✅ Test database created: ics_threat_detection_test"
echo ""
echo "Run tests with: poetry run pytest tests/"
