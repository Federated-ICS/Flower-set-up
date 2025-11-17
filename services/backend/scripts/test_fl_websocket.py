#!/usr/bin/env python3
"""
Test FL WebSocket by calling API endpoints
This works because it goes through the running FastAPI server
"""
import asyncio
import httpx


async def test_fl_websocket():
    """
    Test FL WebSocket integration:
    1. Add 2 facilities at 0%
    2. Update progress gradually
    """
    print("\n" + "=" * 60)
    print("🧪 FL WebSocket Test - 2 Facilities")
    print("=" * 60)
    print("\n📍 Make sure browser is open at:")
    print("   http://localhost:3000/fl-status")
    print("\n⏳ Starting in 3 seconds...")
    await asyncio.sleep(3)

    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Step 1: Initialize 2 facilities at 0%
        print("\n" + "=" * 60)
        print("📍 Step 1: Adding 2 Facilities at 0%")
        print("=" * 60)
        
        init_data = {
            "round_id": 1,
            "round_number": 1,
            "progress": 0,
            "phase": "training",
            "model_accuracy": 0,
            "epsilon": 0.5,
            "clients": [
                {
                    "id": "1",
                    "name": "Facility A",
                    "facility_id": "facility_a",
                    "status": "active",
                    "progress": 0,
                    "current_epoch": 0,
                    "total_epochs": 10,
                },
                {
                    "id": "2",
                    "name": "Facility B",
                    "facility_id": "facility_b",
                    "status": "active",
                    "progress": 0,
                    "current_epoch": 0,
                    "total_epochs": 10,
                },
            ],
        }
        
        response = await client.post(
            f"{base_url}/api/test/custom-fl-progress",
            json=init_data
        )
        
        if response.status_code == 200:
            print("✅ Initialized:")
            print("   - Facility A: 0%")
            print("   - Facility B: 0%")
            print("   - Phase: training")
        else:
            print(f"❌ Error: {response.status_code}")
            return
        
        await asyncio.sleep(2)
        
        # Step 2: Progress through training
        print("\n" + "=" * 60)
        print("📚 Step 2: Training Progress (0% → 100%)")
        print("=" * 60)
        
        for step in range(1, 11):
            progress = step * 10
            epoch = step
            base_accuracy = 70 + (step * 2)
            
            # Determine phase
            if progress < 70:
                phase = "training"
            elif progress < 100:
                phase = "aggregation"
            else:
                phase = "complete"
            
            update_data = {
                "round_id": 1,
                "round_number": 1,
                "progress": progress,
                "phase": phase,
                "model_accuracy": base_accuracy,
                "epsilon": 0.5,
                "clients": [
                    {
                        "id": "1",
                        "name": "Facility A",
                        "facility_id": "facility_a",
                        "status": "active",
                        "progress": min(progress + 5, 100),
                        "loss": max(0.25 - (step * 0.02), 0.05),
                        "accuracy": base_accuracy + 2,
                        "current_epoch": min(epoch, 10),
                        "total_epochs": 10,
                    },
                    {
                        "id": "2",
                        "name": "Facility B",
                        "facility_id": "facility_b",
                        "status": "active",
                        "progress": progress,
                        "loss": max(0.28 - (step * 0.02), 0.08),
                        "accuracy": base_accuracy,
                        "current_epoch": min(epoch, 10),
                        "total_epochs": 10,
                    },
                ],
            }
            
            response = await client.post(
                f"{base_url}/api/test/custom-fl-progress",
                json=update_data
            )
            
            if response.status_code == 200:
                print(f"\n   Step {step}/10 - Progress: {progress}% - Phase: {phase}")
                print(f"   ├─ Facility A: {update_data['clients'][0]['progress']}% | "
                      f"Loss: {update_data['clients'][0]['loss']:.2f} | "
                      f"Acc: {update_data['clients'][0]['accuracy']}%")
                print(f"   └─ Facility B: {update_data['clients'][1]['progress']}% | "
                      f"Loss: {update_data['clients'][1]['loss']:.2f} | "
                      f"Acc: {update_data['clients'][1]['accuracy']}%")
            else:
                print(f"   ❌ Error: {response.status_code}")
            
            await asyncio.sleep(2)
        
        # Final
        print("\n" + "=" * 60)
        print("🎉 Test Complete!")
        print("=" * 60)
        print("\n✅ You should have seen:")
        print("   - 2 facilities (A and B)")
        print("   - Progress: 0% → 100%")
        print("   - Phase: training → aggregation → complete")
        print("   - Real-time updates every 2 seconds")


if __name__ == "__main__":
    asyncio.run(test_fl_websocket())
