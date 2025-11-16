"""
Federated Learning Status API endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.events.emitter import emit_fl_progress
from app.repositories.fl_repository import FLRepository
from app.schemas.fl_status import FLClientSchema, FLRoundResponse, PrivacyMetrics

router = APIRouter()


class ClientUpdateRequest(BaseModel):
    """Request model for updating client progress"""

    status: Optional[str] = None
    progress: Optional[int] = None
    current_epoch: Optional[int] = None
    loss: Optional[float] = None
    accuracy: Optional[float] = None


class RoundProgressRequest(BaseModel):
    """Request model for updating round progress"""

    progress: int
    phase: Optional[str] = None


class CompleteRoundRequest(BaseModel):
    """Request model for completing a round"""

    model_accuracy: float


@router.get("/rounds/current", response_model=Optional[FLRoundResponse])
async def get_current_round(
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current active FL round

    Returns the most recent in-progress round, or null if none exists
    """
    repo = FLRepository(db)
    current_round = await repo.get_current_round()

    if not current_round:
        # Try to get the latest round (even if completed)
        latest = await repo.get_latest_round()
        if not latest:
            return None
        return FLRoundResponse.model_validate(latest)

    return FLRoundResponse.model_validate(current_round)


@router.post("/rounds/trigger", response_model=FLRoundResponse, status_code=status.HTTP_201_CREATED)
async def trigger_fl_round(
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a new FL round

    Creates a new federated learning round with 6 facility clients
    """
    repo = FLRepository(db)

    # Get next round number
    next_round_number = await repo.get_next_round_number()

    # Create new round
    fl_round = await repo.create_round(next_round_number)

    return FLRoundResponse.model_validate(fl_round)


@router.get("/rounds", response_model=dict)
async def get_all_rounds(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all FL rounds with pagination

    Query Parameters:
    - limit: Number of rounds to return (default: 10)
    - offset: Number of rounds to skip (default: 0)
    """
    repo = FLRepository(db)
    rounds = await repo.get_all_rounds(limit=limit, offset=offset)

    return {"rounds": [FLRoundResponse.model_validate(r) for r in rounds]}


@router.get("/rounds/{round_id}", response_model=FLRoundResponse)
async def get_round_by_id(
    round_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific FL round by ID

    Path Parameters:
    - round_id: ID of the FL round
    """
    repo = FLRepository(db)
    fl_round = await repo.get_by_id(round_id)

    if not fl_round:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"FL round with id {round_id} not found"
        )

    return FLRoundResponse.model_validate(fl_round)


@router.put("/rounds/{round_id}/progress", response_model=FLRoundResponse)
async def update_round_progress(
    round_id: int,
    update_data: RoundProgressRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update FL round progress

    Path Parameters:
    - round_id: ID of the FL round

    Body:
    - progress: Progress percentage (0-100)
    - phase: Optional phase (distributing, training, aggregating, complete)
    """
    repo = FLRepository(db)
    fl_round = await repo.update_round_progress(round_id, update_data.progress, update_data.phase)

    if not fl_round:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"FL round with id {round_id} not found"
        )

    # Emit WebSocket event for real-time update
    fl_response = FLRoundResponse.model_validate(fl_round)

    # Log before emitting
    print(f"🔔 Emitting fl_progress event: progress={update_data.progress}%")
    await emit_fl_progress(fl_response.model_dump())
    print("✅ Event emitted successfully")

    return fl_response


@router.post("/rounds/{round_id}/complete", response_model=FLRoundResponse)
async def complete_round(
    round_id: int,
    complete_data: CompleteRoundRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Mark FL round as completed

    Path Parameters:
    - round_id: ID of the FL round

    Body:
    - model_accuracy: Final model accuracy
    """
    repo = FLRepository(db)
    fl_round = await repo.complete_round(round_id, complete_data.model_accuracy)

    if not fl_round:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"FL round with id {round_id} not found"
        )

    return FLRoundResponse.model_validate(fl_round)


@router.get("/clients", response_model=List[FLClientSchema])
async def get_all_clients(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all FL clients from the current round

    Returns list of all facility clients with their current status
    """
    repo = FLRepository(db)
    clients = await repo.get_all_clients()

    return [FLClientSchema.model_validate(client) for client in clients]


@router.get("/clients/{client_id}", response_model=FLClientSchema)
async def get_client_by_id(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific FL client by ID

    Path Parameters:
    - client_id: UUID of the FL client
    """
    repo = FLRepository(db)
    client = await repo.get_client_by_id(client_id)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"FL client with id {client_id} not found"
        )

    return FLClientSchema.model_validate(client)


@router.put("/clients/{client_id}", response_model=FLClientSchema)
async def update_client_status(
    client_id: UUID,
    update_data: ClientUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update FL client status and progress

    Path Parameters:
    - client_id: UUID of the FL client

    Body:
    - status: Optional client status (active, delayed, offline)
    - progress: Optional progress percentage (0-100)
    - current_epoch: Optional current epoch number
    - loss: Optional training loss
    - accuracy: Optional training accuracy
    """
    repo = FLRepository(db)
    client = await repo.update_client_status(
        client_id,
        status=update_data.status,
        progress=update_data.progress,
        current_epoch=update_data.current_epoch,
        loss=update_data.loss,
        accuracy=update_data.accuracy,
    )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"FL client with id {client_id} not found"
        )

    return FLClientSchema.model_validate(client)


@router.get("/privacy-metrics", response_model=PrivacyMetrics)
async def get_privacy_metrics(
    db: AsyncSession = Depends(get_db),
):
    """
    Get privacy metrics for federated learning

    Returns differential privacy parameters and encryption info
    """
    # For now, return static values
    # In production, these would be calculated based on actual FL rounds
    return PrivacyMetrics(
        epsilon=0.5,
        delta="10⁻⁵",
        data_size="~10 MB",
        encryption="AES-256",
        privacy_budget_remaining=85.5,
    )
