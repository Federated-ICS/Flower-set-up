from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.prediction import PredictedTechnique, Prediction
from app.schemas.prediction import PredictionCreate


class PredictionRepository:
    """Repository for Prediction database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, prediction_data: PredictionCreate) -> Prediction:
        """Create a new prediction with predicted techniques"""
        prediction = Prediction(
            current_technique=prediction_data.current_technique,
            current_technique_name=prediction_data.current_technique_name,
            alert_id=prediction_data.alert_id,
            timestamp=datetime.utcnow(),
            validated=False,
        )

        # Add predicted techniques
        for tech_data in prediction_data.predicted_techniques:
            technique = PredictedTechnique(
                technique_id=tech_data.technique_id,
                technique_name=tech_data.technique_name,
                probability=tech_data.probability,
                rank=tech_data.rank,
                timeframe=tech_data.timeframe,
            )
            prediction.predicted_techniques.append(technique)

        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction, ["predicted_techniques"])

        return prediction

    async def get_by_id(self, prediction_id: UUID) -> Optional[Prediction]:
        """Get prediction by ID with predicted techniques"""
        query = (
            select(Prediction)
            .options(selectinload(Prediction.predicted_techniques))
            .where(Prediction.id == prediction_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
        validated: Optional[bool] = None,
    ) -> List[Prediction]:
        """Get all predictions with filtering"""
        query = (
            select(Prediction)
            .options(selectinload(Prediction.predicted_techniques))
            .order_by(Prediction.timestamp.desc())
        )

        if validated is not None:
            query = query.where(Prediction.validated == validated)

        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_latest(self) -> Optional[Prediction]:
        """Get the most recent prediction"""
        query = (
            select(Prediction)
            .options(selectinload(Prediction.predicted_techniques))
            .order_by(Prediction.timestamp.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_alert_id(self, alert_id: UUID) -> List[Prediction]:
        """Get all predictions for a specific alert"""
        query = (
            select(Prediction)
            .options(selectinload(Prediction.predicted_techniques))
            .where(Prediction.alert_id == alert_id)
            .order_by(Prediction.timestamp.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def validate_prediction(self, prediction_id: UUID) -> Optional[Prediction]:
        """Mark a prediction as validated"""
        prediction = await self.get_by_id(prediction_id)
        if not prediction:
            return None

        prediction.validated = True  # type: ignore
        prediction.validation_time = datetime.utcnow()  # type: ignore

        await self.db.commit()
        await self.db.refresh(prediction, ["predicted_techniques"])

        return prediction

    async def delete(self, prediction_id: UUID) -> bool:
        """Delete a prediction"""
        prediction = await self.get_by_id(prediction_id)
        if not prediction:
            return False

        await self.db.delete(prediction)
        await self.db.commit()
        return True
