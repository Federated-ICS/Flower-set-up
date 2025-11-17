"""
Alerts API endpoints
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.events.emitter import emit_alert_created, emit_alert_updated, emit_dashboard_update
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertCreate, AlertResponse, AlertStats, AlertUpdate

router = APIRouter()


@router.get("", response_model=dict)
async def get_alerts(
    severity: Optional[str] = None,
    facility: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    time_range: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all alerts with filtering and pagination

    Query Parameters:
    - severity: Filter by severity (critical, high, medium, low, all)
    - facility: Filter by facility ID
    - status_filter: Filter by status (new, acknowledged, resolved, false-positive)
    - search: Search in title and description
    - time_range: Filter by time (Last 24 hours, Last 7 days, Last 30 days)
    - page: Page number (default: 1)
    - limit: Items per page (default: 10)
    """
    repo = AlertRepository(db)

    alerts, total = await repo.get_all(
        severity=severity,
        facility=facility,
        status=status_filter,
        search=search,
        time_range=time_range,
        page=page,
        limit=limit,
    )

    # Calculate total pages
    pages = (total + limit - 1) // limit if total > 0 else 0

    return {
        "alerts": [AlertResponse.model_validate(alert) for alert in alerts],
        "total": total,
        "page": page,
        "pages": pages,
        "limit": limit,
    }


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new alert

    Body:
    - facility_id: Facility identifier
    - severity: Alert severity (critical, high, medium, low)
    - title: Alert title
    - description: Alert description
    - sources: List of detection sources
    - attack_type: Optional MITRE ATT&CK technique ID
    - attack_name: Optional attack name
    - context_analysis: Optional context analysis data
    """
    repo = AlertRepository(db)
    alert = await repo.create(alert_data)

    # Emit WebSocket event for new alert
    alert_response = AlertResponse.model_validate(alert)
    await emit_alert_created(alert_response.model_dump())

    # Emit updated statistics to dashboard
    stats = await repo.get_stats()
    await emit_dashboard_update({"alertStats": stats.model_dump()})

    return alert_response


@router.get("/stats", response_model=AlertStats)
async def get_alert_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get alert statistics

    Returns:
    - total: Total number of alerts
    - critical: Number of critical alerts
    - unresolved: Number of unresolved alerts (new + acknowledged)
    - false_positives: Number of false positive alerts
    """
    repo = AlertRepository(db)
    stats = await repo.get_stats()
    return stats


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert_by_id(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific alert by ID

    Path Parameters:
    - alert_id: UUID of the alert
    """
    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert with id {alert_id} not found"
        )

    return AlertResponse.model_validate(alert)


@router.put("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: UUID,
    update_data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update alert status

    Path Parameters:
    - alert_id: UUID of the alert

    Body:
    - status: New status (acknowledged, resolved, false-positive)
    """
    repo = AlertRepository(db)
    alert = await repo.update_status(alert_id, update_data.status)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert with id {alert_id} not found"
        )

    # Emit WebSocket event for updated alert
    alert_response = AlertResponse.model_validate(alert)
    await emit_alert_updated(alert_response.model_dump())

    # Emit updated statistics to dashboard
    stats = await repo.get_stats()
    await emit_dashboard_update({"alertStats": stats.model_dump()})

    return alert_response
