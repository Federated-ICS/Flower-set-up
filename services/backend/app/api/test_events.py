"""
Test Events API
Endpoints to trigger WebSocket events for testing
"""
from datetime import datetime

from fastapi import APIRouter

from app.events.emitter import (
    emit_alert_created,
    emit_alert_updated,
    emit_attack_detected,
    emit_dashboard_update,
    emit_fl_progress,
)

router = APIRouter()


@router.post("/test/alert-created")
async def test_alert_created():
    """Trigger a test alert_created event"""
    alert_data = {
        "id": f"test-{datetime.now().timestamp()}",
        "title": "🔴 Real-Time Test Alert",
        "description": "This alert was created via test API endpoint",
        "severity": "critical",
        "facility_id": "facility_a",
        "status": "new",
        "timestamp": datetime.now().isoformat(),
        "sources": [
            {
                "layer": 1,
                "model_name": "Test Model",
                "confidence": 0.95,
                "detection_time": datetime.now().isoformat(),
                "evidence": "API test",
            }
        ],
    }

    await emit_alert_created(alert_data)

    return {
        "success": True,
        "event": "alert_created",
        "data": alert_data,
        "message": "Alert created event emitted. Check /alerts page!",
    }


@router.post("/test/alert-updated")
async def test_alert_updated():
    """Trigger a test alert_updated event"""
    alert_data = {
        "id": "test-alert-001",
        "title": "Updated Test Alert",
        "description": "This alert was updated via test API",
        "severity": "high",
        "facility_id": "facility_a",
        "status": "acknowledged",
        "timestamp": datetime.now().isoformat(),
        "sources": [],
    }

    await emit_alert_updated(alert_data)

    return {
        "success": True,
        "event": "alert_updated",
        "data": alert_data,
        "message": "Alert updated event emitted. Check /alerts page!",
    }


@router.post("/test/fl-progress")
async def test_fl_progress():
    """Trigger a test fl_progress event"""
    progress_data = {
        "round_id": 1,
        "round_number": 42,
        "progress": 85,
        "phase": "aggregation",
        "model_accuracy": 94.5,
        "clients": [
            {
                "id": "1",
                "name": "Facility A",
                "facility_id": "facility_a",
                "status": "active",
                "progress": 100,
                "loss": 0.08,
                "accuracy": 96.2,
                "current_epoch": 10,
                "total_epochs": 10,
            }
        ],
    }

    await emit_fl_progress(progress_data)

    return {
        "success": True,
        "event": "fl_progress",
        "data": progress_data,
        "message": "FL progress event emitted. Check /fl-status page!",
    }


@router.post("/test/attack-detected")
async def test_attack_detected(data: dict | None = None):
    """Trigger a test attack_detected event

    Supports both current attacks and predicted techniques:
    - type: "current" for detected attacks
    - type: "predicted" for predicted future techniques
    - source_technique_id: optional, creates a link from source to this technique
    - links: optional array of {source, target, probability} for multiple links
    """
    # Use provided data or default test data
    if data:
        attack_data = {
            "technique_id": data.get("technique_id", "T0802"),
            "technique_name": data.get("technique_name", "Test Attack"),
            "confidence": data.get("confidence", 0.92),
            "type": data.get("type", "current"),  # Support "current" or "predicted"
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "facility_id": data.get("facility_id", "facility_a"),
            "evidence": data.get("evidence", "API test detection"),
        }

        # Add link information if provided
        if "source_technique_id" in data:
            attack_data["source_technique_id"] = data["source_technique_id"]
            attack_data["link_probability"] = data.get(
                "link_probability", data.get("confidence", 0.5)
            )

        # Add multiple links if provided
        if "links" in data:
            attack_data["links"] = data["links"]
    else:
        attack_data = {
            "technique_id": "T0802",
            "technique_name": "Automated Collection (Test)",
            "confidence": 0.92,
            "type": "current",
            "timestamp": datetime.now().isoformat(),
            "facility_id": "facility_a",
            "evidence": "API test detection",
        }

    await emit_attack_detected(attack_data)

    return {
        "success": True,
        "event": "attack_detected",
        "data": attack_data,
        "message": "Attack detected event emitted. Check /attack-graph page!",
    }


@router.post("/test/dashboard-update")
async def test_dashboard_update():
    """Trigger a test dashboard_update event"""
    stats_data = {
        "alertStats": {
            "total": 25,
            "critical": 8,
            "unresolved": 15,
            "false_positives": 2,
        },
        "flStatus": {
            "round_number": 42,
            "progress": 85,
            "model_accuracy": 95.2,
        },
    }

    await emit_dashboard_update(stats_data)

    return {
        "success": True,
        "event": "dashboard_update",
        "data": stats_data,
        "message": "Dashboard update event emitted. Check dashboard!",
    }


@router.post("/test/custom-fl-progress")
async def test_custom_fl_progress(data: dict):
    """Trigger a custom FL progress event with provided data"""
    await emit_fl_progress(data)

    return {
        "success": True,
        "event": "fl_progress",
        "data": data,
        "message": "Custom FL progress event emitted. Check /fl-status page!",
    }
