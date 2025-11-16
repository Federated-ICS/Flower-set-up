#!/usr/bin/env python3
"""
Test script for Attack Graph WebSocket events
Sends various attack detection events to test real-time updates

Usage:
    poetry run python scripts/test_attack_graph.py
"""
import asyncio
import httpx
from datetime import datetime


BASE_URL = "http://localhost:8000"


async def send_attack_event(technique_id: str, technique_name: str, confidence: float, facility_id: str, evidence: str):
    """Send an attack detection event via API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/test/attack-detected",
            json={
                "technique_id": technique_id,
                "technique_name": technique_name,
                "confidence": confidence,
                "facility_id": facility_id,
                "evidence": evidence,
                "timestamp": datetime.now().isoformat(),
            },
            timeout=10.0,
        )
        return response.json()


async def main():
    print("🎯 Testing Attack Graph WebSocket Events")
    print("=" * 50)
    print()
    print("Make sure:")
    print("1. Backend is running (uvicorn app.main:app --reload)")
    print("2. Frontend is running (npm run dev)")
    print("3. Attack Graph page is open in browser (/attack-graph)")
    print()
    input("Press Enter to start sending attack events...")
    print()

    # Test scenarios
    attacks = [
        {
            "technique_id": "T0842",
            "technique_name": "Network Sniffing",
            "confidence": 0.87,
            "facility_id": "facility_a",
            "evidence": "Suspicious network traffic detected on SCADA network",
            "description": "Initial Reconnaissance",
        },
        {
            "technique_id": "T0867",
            "technique_name": "Lateral Tool Transfer",
            "confidence": 0.92,
            "facility_id": "facility_b",
            "evidence": "Unauthorized file transfer between PLCs",
            "description": "Lateral Movement",
        },
        {
            "technique_id": "T0871",
            "technique_name": "Execution through API",
            "confidence": 0.95,
            "facility_id": "facility_a",
            "evidence": "Malicious API calls to control system",
            "description": "Execution Phase",
        },
        {
            "technique_id": "T0826",
            "technique_name": "Loss of View",
            "confidence": 0.98,
            "facility_id": "facility_c",
            "evidence": "HMI display manipulation detected",
            "description": "Impact - High Confidence",
        },
        {
            "technique_id": "T0842",
            "technique_name": "Network Sniffing",
            "confidence": 0.96,
            "facility_id": "facility_a",
            "evidence": "Additional evidence: Deep packet inspection reveals data exfiltration",
            "description": "Update existing with higher confidence",
        },
    ]

    for i, attack in enumerate(attacks, 1):
        print(f"{i}️⃣  {attack['description']}: {attack['technique_id']} - {attack['technique_name']}")
        print(f"   Confidence: {attack['confidence']:.0%} | Facility: {attack['facility_id']}")
        
        result = await send_attack_event(
            technique_id=attack["technique_id"],
            technique_name=attack["technique_name"],
            confidence=attack["confidence"],
            facility_id=attack["facility_id"],
            evidence=attack["evidence"],
        )
        
        if result.get("success"):
            print(f"   ✅ Event emitted successfully")
        else:
            print(f"   ❌ Failed: {result}")
        
        print()
        await asyncio.sleep(2)

    print()
    print("✅ All attack events sent!")
    print()
    print("Check your Attack Graph page - you should see:")
    print("  • New nodes appearing in real-time")
    print("  • Updated confidence levels")
    print("  • Current Attacks counter increasing")
    print("  • Graph automatically updating without refresh")
    print()


if __name__ == "__main__":
    asyncio.run(main())
