"""
Predictions API endpoints
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.prediction import PredictionCreate, PredictionResponse

router = APIRouter()


@router.get("", response_model=dict)
async def get_predictions(
    limit: int = 10,
    offset: int = 0,
    validated: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all predictions with filtering

    Query Parameters:
    - limit: Number of predictions to return (default: 10)
    - offset: Number of predictions to skip (default: 0)
    - validated: Filter by validation status (true/false)
    """
    repo = PredictionRepository(db)
    predictions = await repo.get_all(
        limit=limit,
        offset=offset,
        validated=validated,
    )

    return {"predictions": [PredictionResponse.model_validate(p) for p in predictions]}


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    prediction_data: PredictionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new attack prediction

    Body:
    - current_technique: Current MITRE ATT&CK technique ID
    - current_technique_name: Current technique name
    - alert_id: Associated alert UUID
    - predicted_techniques: List of predicted next techniques with probabilities
    """
    repo = PredictionRepository(db)
    prediction = await repo.create(prediction_data)
    return PredictionResponse.model_validate(prediction)


@router.get("/latest", response_model=Optional[PredictionResponse])
async def get_latest_prediction(
    db: AsyncSession = Depends(get_db),
):
    """
    Get the most recent prediction

    Returns the latest prediction or null if none exists
    """
    repo = PredictionRepository(db)
    prediction = await repo.get_latest()

    if not prediction:
        return None

    return PredictionResponse.model_validate(prediction)


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction_by_id(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific prediction by ID

    Path Parameters:
    - prediction_id: UUID of the prediction
    """
    repo = PredictionRepository(db)
    prediction = await repo.get_by_id(prediction_id)

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with id {prediction_id} not found",
        )

    return PredictionResponse.model_validate(prediction)


@router.post("/{prediction_id}/validate", response_model=PredictionResponse)
async def validate_prediction(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a prediction as validated

    Path Parameters:
    - prediction_id: UUID of the prediction

    This endpoint is called when a predicted attack actually occurs,
    confirming the accuracy of the prediction.
    """
    repo = PredictionRepository(db)
    prediction = await repo.validate_prediction(prediction_id)

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with id {prediction_id} not found",
        )

    return PredictionResponse.model_validate(prediction)
