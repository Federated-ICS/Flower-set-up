"""
Seed database with mock data for development and demo
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime, timedelta
import random
from uuid import uuid4

from app.database import async_session_maker
from app.repositories.alert_repository import AlertRepository
from app.repositories.fl_repository import FLRepository
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.alert import AlertCreate, AlertSourceSchema
from app.schemas.prediction import PredictionCreate, PredictedTechniqueSchema


async def seed_alerts(db):
    """Seed alert data"""
    print("📊 Seeding alerts...")
    
    repo = AlertRepository(db)
    
    facilities = ["facility_a", "facility_b", "facility_c", "facility_d", "facility_e", "facility_f"]
    severities = ["critical", "high", "medium", "low"]
    statuses = ["new", "acknowledged", "resolved"]
    
    alert_templates = [
        {
            "title": "Port Scan Detected",
            "description": "Unusual port scanning activity detected from external IP",
            "attack_type": "T0846",
            "attack_name": "Port Scan",
            "severity": "high",
        },
        {
            "title": "Brute Force Login Attempt",
            "description": "Multiple failed login attempts detected on HMI interface",
            "attack_type": "T0859",
            "attack_name": "Brute Force",
            "severity": "critical",
        },
        {
            "title": "Unusual Modbus Traffic",
            "description": "Abnormal Modbus protocol behavior detected",
            "attack_type": "T0885",
            "attack_name": "Protocol Manipulation",
            "severity": "high",
        },
        {
            "title": "Unauthorized Device Connection",
            "description": "Unknown device attempting to connect to SCADA network",
            "attack_type": "T0817",
            "attack_name": "Unauthorized Access",
            "severity": "critical",
        },
        {
            "title": "DNS Tunneling Detected",
            "description": "Suspicious DNS query patterns indicating data exfiltration",
            "attack_type": "T0567",
            "attack_name": "Data Exfiltration",
            "severity": "high",
        },
        {
            "title": "Anomalous Network Traffic",
            "description": "Unusual spike in network traffic volume",
            "attack_type": "T0800",
            "attack_name": "Network Anomaly",
            "severity": "medium",
        },
        {
            "title": "Failed Connection Spike",
            "description": "High number of failed connection attempts",
            "attack_type": "T0846",
            "attack_name": "Reconnaissance",
            "severity": "medium",
        },
        {
            "title": "Malformed Packet Detected",
            "description": "Packets with invalid headers detected",
            "attack_type": "T0885",
            "attack_name": "Protocol Exploit",
            "severity": "high",
        },
    ]
    
    created_alerts = []
    
    for i in range(20):
        template = random.choice(alert_templates)
        timestamp = datetime.utcnow() - timedelta(hours=random.randint(0, 48))
        
        # Create sources (detection layers)
        sources = []
        
        # Layer 1: Anomaly detection
        if random.random() > 0.3:
            sources.append(AlertSourceSchema(
                layer=1,
                model_name=random.choice(["LSTM Autoencoder", "Isolation Forest"]),
                confidence=random.uniform(0.7, 0.95),
                detection_time=timestamp,
                evidence=f"Anomaly score: {random.uniform(0.8, 0.99):.2f}",
                context_evidence={
                    "packets_per_sec": random.randint(100, 500),
                    "unique_dest_ips": random.randint(10, 50),
                }
            ))
        
        # Layer 2: Classification
        if random.random() > 0.5:
            sources.append(AlertSourceSchema(
                layer=2,
                model_name="Threat Classifier",
                confidence=random.uniform(0.75, 0.98),
                detection_time=timestamp + timedelta(seconds=5),
                evidence=f"Attack type: {template['attack_type']}",
                context_evidence={
                    "pattern_match": "high",
                    "behavior_score": random.uniform(0.7, 0.95),
                }
            ))
        
        alert_data = AlertCreate(
            facility_id=random.choice(facilities),
            severity=template["severity"],
            title=template["title"],
            description=template["description"],
            attack_type=template.get("attack_type"),
            attack_name=template.get("attack_name"),
            sources=sources,
        )
        
        alert = await repo.create(alert_data)
        created_alerts.append(alert)
        
        # Update some to different statuses
        if i > 5 and random.random() > 0.5:
            status = random.choice(statuses)
            await repo.update_status(alert.id, status)
    
    print(f"✅ Created {len(created_alerts)} alerts")
    return created_alerts


async def seed_fl_rounds(db):
    """Seed FL round data"""
    print("🔄 Seeding FL rounds...")
    
    repo = FLRepository(db)
    
    # Create 3 completed rounds
    for round_num in range(1, 4):
        fl_round = await repo.create_round(round_num)
        
        # Update clients with completed data
        for client in fl_round.clients:
            await repo.update_client_status(
                client.id,
                status="active",
                progress=100,
                current_epoch=10,
                loss=random.uniform(0.05, 0.15),
                accuracy=random.uniform(92.0, 96.0),
            )
        
        # Complete the round
        await repo.complete_round(
            fl_round.id,
            model_accuracy=random.uniform(93.0, 96.5),
        )
    
    # Create 1 in-progress round
    current_round_num = await repo.get_next_round_number()
    current_round = await repo.create_round(current_round_num)
    
    # Update clients with partial progress
    for i, client in enumerate(current_round.clients):
        await repo.update_client_status(
            client.id,
            status=random.choice(["active", "active", "delayed"]),
            progress=random.randint(40, 80),
            current_epoch=random.randint(4, 8),
            loss=random.uniform(0.08, 0.18),
            accuracy=random.uniform(88.0, 94.0),
        )
    
    # Update round progress
    await repo.update_round_progress(
        current_round.id,
        progress=random.randint(50, 75),
        phase="training",
    )
    
    print(f"✅ Created {current_round_num} FL rounds")
    return current_round


async def seed_predictions(db, alerts):
    """Seed prediction data"""
    print("🎯 Seeding predictions...")
    
    repo = PredictionRepository(db)
    
    # MITRE ATT&CK technique relationships
    technique_chains = [
        {
            "current": ("T0846", "Port Scan"),
            "next": [
                ("T0800", "Lateral Movement", 0.72),
                ("T0817", "Unauthorized Access", 0.65),
                ("T0859", "Brute Force", 0.58),
            ]
        },
        {
            "current": ("T0859", "Brute Force"),
            "next": [
                ("T0817", "Unauthorized Access", 0.78),
                ("T0800", "Lateral Movement", 0.68),
                ("T0890", "Privilege Escalation", 0.55),
            ]
        },
        {
            "current": ("T0885", "Protocol Manipulation"),
            "next": [
                ("T0836", "Command Injection", 0.70),
                ("T0800", "Lateral Movement", 0.62),
                ("T0809", "Data Manipulation", 0.58),
            ]
        },
    ]
    
    created_predictions = []
    
    # Create predictions for some alerts
    for alert in alerts[:10]:
        if alert.attack_type:
            # Find matching technique chain
            chain = next(
                (c for c in technique_chains if c["current"][0] == alert.attack_type),
                technique_chains[0]  # Default
            )
            
            predicted_techniques = [
                PredictedTechniqueSchema(
                    technique_id=tech[0],
                    technique_name=tech[1],
                    probability=tech[2],
                    rank=idx + 1,
                    timeframe="15-60 minutes" if idx == 0 else "1-4 hours",
                )
                for idx, tech in enumerate(chain["next"])
            ]
            
            prediction_data = PredictionCreate(
                current_technique=chain["current"][0],
                current_technique_name=chain["current"][1],
                alert_id=alert.id,
                predicted_techniques=predicted_techniques,
            )
            
            prediction = await repo.create(prediction_data)
            created_predictions.append(prediction)
            
            # Validate some predictions
            if random.random() > 0.6:
                await repo.validate_prediction(prediction.id)
    
    print(f"✅ Created {len(created_predictions)} predictions")
    return created_predictions


async def main():
    """Main seed function"""
    print("🌱 Starting database seeding...")
    print()
    
    async with async_session_maker() as db:
        try:
            # Seed data
            alerts = await seed_alerts(db)
            fl_round = await seed_fl_rounds(db)
            predictions = await seed_predictions(db, alerts)
            
            print()
            print("✅ Database seeding completed successfully!")
            print()
            print("📊 Summary:")
            print(f"  - Alerts: {len(alerts)}")
            print(f"  - FL Rounds: 4 (3 completed, 1 in-progress)")
            print(f"  - Predictions: {len(predictions)}")
            print()
            
        except Exception as e:
            print(f"❌ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
