#!/bin/bash

echo "🧪 Testing ICS Threat Detection API"
echo "===================================="
echo ""

BASE_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Health Check${NC}"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

echo -e "${BLUE}2. Alert Statistics${NC}"
curl -s "$BASE_URL/api/alerts/stats" | python -m json.tool
echo ""

echo -e "${BLUE}3. Recent Alerts (3)${NC}"
curl -s "$BASE_URL/api/alerts?limit=3" | python -m json.tool | head -50
echo ""

echo -e "${BLUE}4. Filter Critical Alerts${NC}"
curl -s "$BASE_URL/api/alerts?severity=critical&limit=2" | python -m json.tool | head -30
echo ""

echo -e "${BLUE}5. Current FL Round${NC}"
curl -s "$BASE_URL/api/fl/rounds/current" | python -m json.tool | head -25
echo ""

echo -e "${BLUE}6. FL Clients Status${NC}"
curl -s "$BASE_URL/api/fl/clients" | python -m json.tool | head -30
echo ""

echo -e "${BLUE}7. FL Privacy Metrics${NC}"
curl -s "$BASE_URL/api/fl/privacy-metrics" | python -m json.tool
echo ""

echo -e "${BLUE}8. Latest Prediction${NC}"
curl -s "$BASE_URL/api/predictions/latest" | python -m json.tool | head -30
echo ""

echo -e "${BLUE}9. All Predictions${NC}"
curl -s "$BASE_URL/api/predictions?limit=3" | python -m json.tool | head -40
echo ""

echo -e "${GREEN}✅ API Test Complete!${NC}"
echo ""
echo "📖 Interactive API Docs: http://localhost:8000/docs"
echo "📊 Alternative Docs: http://localhost:8000/redoc"
