"""
Test script to verify repositories work correctly
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import async_session_maker
from app.repositories.alert_repository import AlertRepository
from app.repositories.fl_repository import FLRepository
from app.repositories.prediction_repository import PredictionRepository


async def test_repositories():
    """Test all repositories"""
    print("🧪 Testing repositories...")
    print()
    
    async with async_session_maker() as db:
        # Test Alert Repository
        print("1️⃣ Testing AlertRepository...")
        alert_repo = AlertRepository(db)
        
        alerts, total = await alert_repo.get_all(limit=5)
        print(f"   ✅ Found {total} total alerts")
        print(f"   ✅ Retrieved {len(alerts)} alerts")
        
        if alerts:
            alert = alerts[0]
            print(f"   ✅ First alert: {alert.title}")
            print(f"      - Severity: {alert.severity}")
            print(f"      - Facility: {alert.facility_id}")
            print(f"      - Sources: {len(alert.sources)}")
        
        stats = await alert_repo.get_stats()
        print(f"   ✅ Stats: {stats.total} total, {stats.critical} critical, {stats.unresolved} unresolved")
        print()
        
        # Test FL Repository
        print("2️⃣ Testing FLRepository...")
        fl_repo = FLRepository(db)
        
        current_round = await fl_repo.get_current_round()
        if current_round:
            print(f"   ✅ Current round: #{current_round.round_number}")
            print(f"      - Status: {current_round.status}")
            print(f"      - Phase: {current_round.phase}")
            print(f"      - Progress: {current_round.progress}%")
            print(f"      - Clients: {len(current_round.clients)}")
        else:
            print("   ⚠️  No current round found")
        
        all_rounds = await fl_repo.get_all_rounds(limit=5)
        print(f"   ✅ Found {len(all_rounds)} FL rounds")
        print()
        
        # Test Prediction Repository
        print("3️⃣ Testing PredictionRepository...")
        pred_repo = PredictionRepository(db)
        
        predictions = await pred_repo.get_all(limit=5)
        print(f"   ✅ Found {len(predictions)} predictions")
        
        if predictions:
            pred = predictions[0]
            print(f"   ✅ First prediction: {pred.current_technique_name}")
            print(f"      - Predicted techniques: {len(pred.predicted_techniques)}")
            if pred.predicted_techniques:
                top = pred.predicted_techniques[0]
                print(f"      - Top prediction: {top.technique_name} ({top.probability:.2%})")
        print()
        
        print("✅ All repository tests passed!")


if __name__ == "__main__":
    asyncio.run(test_repositories())
