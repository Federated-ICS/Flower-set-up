#!/usr/bin/env python3
"""
Seed Database Script
Populates the FedICS database with sample data for testing and development.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.streaming.event_models import AnomalyEvent, AttackPrediction


async def main():
    print("🌱 Seeding FedICS database with sample data...")
    print()
    
    # Import database models
    try:
        # Check if backend exists
        backend_path = Path(__file__).parent.parent / "services" / "backend"
        if not backend_path.exists():
            print("❌ Backend not found at services/backend/")
            print("💡 Please ensure backend consolidation is complete.")
            return
        
        # Add backend to path
        sys.path.insert(0, str(backend_path))
        
        from app.database import async_session
        from app.models.alert import Alert, AlertSource
        from app.models.fl_round import FLRound, FLClient
        from app.models.prediction import Prediction, PredictedTechnique
        from app.models.network_data import NetworkData
        
        print("✓ Database models imported")
    except ImportError as e:
        print(f"❌ Error importing backend modules: {e}")
        print("💡 Make sure backend dependencies are installed:")
        print("   cd services/backend && poetry install")
        return
    
    async with async_session() as session:
        print()
        print("📊 Creating sample network data...")
        
        # Sample network packets
        for i in range(50):
            packet = NetworkData(
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 120)),
                source_ip=f"192.168.1.{random.randint(1, 254)}",
                dest_ip=f"10.0.0.{random.randint(1, 254)}",
                source_port=random.randint(1024, 65535),
                dest_port=random.choice([80, 443, 502, 20000, 47808]),  # Mix of common and ICS ports
                protocol=random.choice(["TCP", "UDP", "Modbus/TCP", "DNP3"]),
                payload_size=random.randint(64, 1500),
                flags=random.choice(["SYN", "ACK", "PSH", "FIN", None])
            )
            session.add(packet)
        
        print("✓ Created 50 network packets")
        
        print()
        print("🚨 Creating sample alerts...")
        
        # Sample alerts
        alert_types = [
            ("DDoS Attack Detected", "HIGH", "MITRE T0814: Denial of Service"),
            ("Unauthorized Access Attempt", "CRITICAL", "MITRE T0822: Manipulation of View"),
            ("Anomalous Modbus Traffic", "MEDIUM", "MITRE T0801: Command and Control"),
            ("Lateral Movement Detected", "HIGH", "MITRE T0867: Lateral Movement"),
            ("Data Exfiltration", "CRITICAL", "MITRE T0802: Data from Information Repositories")
        ]
        
        for i, (title, severity, technique) in enumerate(alert_types * 4):  # 20 alerts
            alert = Alert(
                title=title,
                severity=severity,
                facility=random.choice(["Facility_A", "Facility_B", "Facility_C"]),
                technique_id=technique.split(":")[0].split()[-1],  # Extract T-code
                technique_name=technique.split(": ")[1],
                status=random.choice(["active", "investigating", "resolved"]),
                confidence=random.uniform(0.7, 0.99),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                raw_event={
                    "source": random.choice(["lstm_autoencoder", "isolation_forest", "physics_rules"]),
                    "anomaly_score": random.uniform(0.7, 0.95)
                }
            )
            
            # Add alert sources
            for source_type in random.sample(["lstm_autoencoder", "isolation_forest", "physics_rules"], k=2):
                source = AlertSource(
                    alert=alert,
                    detector_type=source_type,
                    confidence=random.uniform(0.65, 0.95),
                    detected_at=alert.timestamp
                )
                session.add(source)
            
            session.add(alert)
        
        print("✓ Created 20 alerts with detection sources")
        
        print()
        print("🤝 Creating federated learning rounds...")
        
        # FL rounds
        for i in range(5):
            round_num = i + 1
            fl_round = FLRound(
                round_number=round_num,
                status=random.choice(["completed", "in_progress", "failed"]) if i < 4 else "in_progress",
                start_time=datetime.utcnow() - timedelta(hours=24-i*4),
                end_time=datetime.utcnow() - timedelta(hours=20-i*4) if i < 4 else None,
                num_clients=3,
                aggregated_metrics={
                    "accuracy": random.uniform(0.85, 0.95),
                    "loss": random.uniform(0.05, 0.15),
                    "epsilon": 0.5 * round_num  # Cumulative privacy budget
                }
            )
            
            # Add FL clients for this round
            for client_id in range(3):
                client = FLClient(
                    fl_round=fl_round,
                    client_id=f"client_{client_id}",
                    facility=["Facility_A", "Facility_B", "Facility_C"][client_id],
                    model_type=["lstm_autoencoder", "lstm_autoencoder", "isolation_forest"][client_id],
                    num_samples=random.randint(1000, 5000),
                    metrics={
                        "local_accuracy": random.uniform(0.80, 0.95),
                        "local_loss": random.uniform(0.05, 0.20),
                        "training_time_seconds": random.uniform(30, 120)
                    },
                    privacy_epsilon=0.5
                )
                session.add(client)
            
            session.add(fl_round)
        
        print("✓ Created 5 FL rounds with 15 client records")
        
        print()
        print("🔮 Creating attack predictions...")
        
        # Attack predictions
        attack_patterns = [
            (["T0814", "T0801", "T0822"], "DDoS + C2 + Manipulation"),
            (["T0822", "T0867", "T0802"], "View Manipulation + Lateral Movement + Exfiltration"),
            (["T0801", "T0814"], "Command & Control + DoS"),
            (["T0867", "T0802"], "Lateral Movement + Data Theft")
        ]
        
        for i, (techniques, description) in enumerate(attack_patterns * 3):  # 12 predictions
            prediction = Prediction(
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                facility=random.choice(["Facility_A", "Facility_B", "Facility_C"]),
                attack_vector=description,
                confidence=random.uniform(0.75, 0.95),
                severity_score=random.uniform(0.6, 0.9),
                is_validated=random.choice([True, False, None])
            )
            
            # Add predicted techniques
            for tech_id in techniques:
                predicted_tech = PredictedTechnique(
                    prediction=prediction,
                    technique_id=tech_id,
                    probability=random.uniform(0.7, 0.95),
                    rationale=f"Correlation with previous alerts and network patterns"
                )
                session.add(predicted_tech)
            
            session.add(prediction)
        
        print("✓ Created 12 attack predictions with technique forecasts")
        
        # Commit all changes
        print()
        print("💾 Committing to database...")
        await session.commit()
        
        print()
        print("✅ Database seeding complete!")
        print()
        print("📊 Summary:")
        print("   • 50 network packets")
        print("   • 20 alerts with detection sources")
        print("   • 5 FL rounds with 15 client records")
        print("   • 12 attack predictions")
        print()
        print("🌐 View data at:")
        print("   • API: http://localhost:8000/docs")
        print("   • Dashboard: http://localhost:3000")
        print()


if __name__ == "__main__":
    asyncio.run(main())
