from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert, AlertSource, SeverityEnum, StatusEnum
from app.schemas.alert import AlertCreate, AlertStats


class AlertRepository:
    """Repository for Alert database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, alert_data: AlertCreate) -> Alert:
        """Create a new alert with sources"""
        # Create alert
        alert = Alert(
            facility_id=alert_data.facility_id,
            severity=alert_data.severity,
            title=alert_data.title,
            description=alert_data.description,
            attack_type=alert_data.attack_type,
            attack_name=alert_data.attack_name,
            context_analysis=alert_data.context_analysis.dict()
            if alert_data.context_analysis
            else None,
            timestamp=datetime.utcnow(),
            status=StatusEnum.new,
        )

        # Add sources
        for source_data in alert_data.sources:
            source = AlertSource(
                layer=source_data.layer,
                model_name=source_data.model_name,
                confidence=source_data.confidence,
                detection_time=source_data.detection_time,
                evidence=source_data.evidence,
                context_evidence=source_data.context_evidence,
            )
            alert.sources.append(source)

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert, ["sources"])  # Eagerly load sources

        return alert

    async def get_by_id(self, alert_id: UUID) -> Optional[Alert]:
        """Get alert by ID with sources"""
        query = select(Alert).options(selectinload(Alert.sources)).where(Alert.id == alert_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        severity: Optional[str] = None,
        facility: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        time_range: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[Alert], int]:
        """Get alerts with filtering and pagination"""

        # Build base query
        query = select(Alert).options(selectinload(Alert.sources))

        # Apply filters
        filters = []

        if severity and severity != "all":
            filters.append(Alert.severity == severity)

        if facility and facility != "All Facilities":
            filters.append(Alert.facility_id == facility)

        if status:
            filters.append(Alert.status == status)

        if search:
            search_filter = or_(
                Alert.title.ilike(f"%{search}%"),
                Alert.description.ilike(f"%{search}%"),
            )
            filters.append(search_filter)

        if time_range:
            now = datetime.utcnow()
            if time_range == "Last 24 hours":
                filters.append(Alert.timestamp >= now - timedelta(hours=24))
            elif time_range == "Last 7 days":
                filters.append(Alert.timestamp >= now - timedelta(days=7))
            elif time_range == "Last 30 days":
                filters.append(Alert.timestamp >= now - timedelta(days=30))

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(Alert)
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Alert.timestamp.desc()).offset((page - 1) * limit).limit(limit)

        result = await self.db.execute(query)
        alerts = result.scalars().all()

        return list(alerts), total

    async def update_status(self, alert_id: UUID, status: str) -> Optional[Alert]:
        """Update alert status"""
        alert = await self.get_by_id(alert_id)
        if not alert:
            return None

        alert.status = StatusEnum(status)  # type: ignore
        await self.db.commit()
        await self.db.refresh(alert, ["sources"])  # Eagerly load sources

        return alert

    async def get_stats(self) -> AlertStats:
        """Calculate alert statistics"""
        # Total alerts
        total_query = select(func.count()).select_from(Alert)
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0

        # Critical alerts
        critical_query = (
            select(func.count()).select_from(Alert).where(Alert.severity == SeverityEnum.critical)
        )
        critical_result = await self.db.execute(critical_query)
        critical = critical_result.scalar() or 0

        # Unresolved alerts
        unresolved_query = (
            select(func.count())
            .select_from(Alert)
            .where(Alert.status.in_([StatusEnum.new, StatusEnum.acknowledged]))
        )
        unresolved_result = await self.db.execute(unresolved_query)
        unresolved = unresolved_result.scalar() or 0

        # False positives
        fp_query = (
            select(func.count()).select_from(Alert).where(Alert.status == StatusEnum.false_positive)
        )
        fp_result = await self.db.execute(fp_query)
        false_positives = fp_result.scalar() or 0

        return AlertStats(
            total=total,
            critical=critical,
            unresolved=unresolved,
            false_positives=false_positives,
        )

    async def delete(self, alert_id: UUID) -> bool:
        """Delete an alert"""
        alert = await self.get_by_id(alert_id)
        if not alert:
            return False

        await self.db.delete(alert)
        await self.db.commit()
        return True
