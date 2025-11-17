from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.fl_round import ClientStatusEnum, FLClient, FLRound, PhaseEnum, RoundStatusEnum


class FLRepository:
    """Repository for Federated Learning database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_round(self, round_number: int) -> FLRound:
        """Create a new FL round"""
        fl_round = FLRound(
            round_number=round_number,
            status=RoundStatusEnum.in_progress,
            phase=PhaseEnum.distributing,
            start_time=datetime.utcnow(),
            progress=0,
            epsilon=0.5,
            clients_active=0,
            total_clients=2,
        )

        # Create clients for each facility
        facilities = [
            ("facility_a", "Facility A"),
            ("facility_b", "Facility B"),
        ]

        for facility_id, name in facilities:
            client = FLClient(
                facility_id=facility_id,
                name=name,
                status=ClientStatusEnum.active,
                progress=0,
                current_epoch=0,
                total_epochs=10,
                last_update=datetime.utcnow(),
            )
            fl_round.clients.append(client)

        self.db.add(fl_round)
        await self.db.commit()
        await self.db.refresh(fl_round, ["clients"])

        return fl_round

    async def get_by_id(self, round_id: int) -> Optional[FLRound]:
        """Get FL round by ID with clients"""
        query = select(FLRound).options(selectinload(FLRound.clients)).where(FLRound.id == round_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_round_number(self, round_number: int) -> Optional[FLRound]:
        """Get FL round by round number"""
        query = (
            select(FLRound)
            .options(selectinload(FLRound.clients))
            .where(FLRound.round_number == round_number)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_current_round(self) -> Optional[FLRound]:
        """Get the current active FL round"""
        query = (
            select(FLRound)
            .options(selectinload(FLRound.clients))
            .where(FLRound.status == RoundStatusEnum.in_progress)
            .order_by(FLRound.round_number.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_latest_round(self) -> Optional[FLRound]:
        """Get the most recent FL round (active or completed)"""
        query = (
            select(FLRound)
            .options(selectinload(FLRound.clients))
            .order_by(FLRound.round_number.desc())
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_rounds(self, limit: int = 10, offset: int = 0) -> List[FLRound]:
        """Get all FL rounds with pagination"""
        query = (
            select(FLRound)
            .options(selectinload(FLRound.clients))
            .order_by(FLRound.round_number.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_round_progress(
        self,
        round_id: int,
        progress: int,
        phase: Optional[str] = None,
    ) -> Optional[FLRound]:
        """Update FL round progress"""
        fl_round = await self.get_by_id(round_id)
        if not fl_round:
            return None

        fl_round.progress = progress  # type: ignore
        if phase:
            fl_round.phase = PhaseEnum(phase)  # type: ignore

        await self.db.commit()
        await self.db.refresh(fl_round, ["clients"])

        return fl_round

    async def complete_round(
        self,
        round_id: int,
        model_accuracy: float,
    ) -> Optional[FLRound]:
        """Mark FL round as completed"""
        fl_round = await self.get_by_id(round_id)
        if not fl_round:
            return None

        fl_round.status = RoundStatusEnum.completed  # type: ignore
        fl_round.phase = PhaseEnum.complete  # type: ignore
        fl_round.progress = 100  # type: ignore
        fl_round.end_time = datetime.utcnow()  # type: ignore
        fl_round.model_accuracy = model_accuracy  # type: ignore

        await self.db.commit()
        await self.db.refresh(fl_round, ["clients"])

        return fl_round

    async def get_all_clients(self) -> List[FLClient]:
        """Get all FL clients from current round"""
        current_round = await self.get_current_round()
        if not current_round:
            return []
        return list(current_round.clients)

    async def get_client_by_id(self, client_id: UUID) -> Optional[FLClient]:
        """Get FL client by ID"""
        query = select(FLClient).where(FLClient.id == client_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_client_status(
        self,
        client_id: UUID,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        current_epoch: Optional[int] = None,
        loss: Optional[float] = None,
        accuracy: Optional[float] = None,
    ) -> Optional[FLClient]:
        """Update FL client status"""
        client = await self.get_client_by_id(client_id)
        if not client:
            return None

        if status:
            client.status = ClientStatusEnum(status)  # type: ignore
        if progress is not None:
            client.progress = progress  # type: ignore
        if current_epoch is not None:
            client.current_epoch = current_epoch  # type: ignore
        if loss is not None:
            client.loss = loss  # type: ignore
        if accuracy is not None:
            client.accuracy = accuracy  # type: ignore

        client.last_update = datetime.utcnow()  # type: ignore

        await self.db.commit()
        # No relationships to refresh for client

        return client

    async def get_next_round_number(self) -> int:
        """Get the next round number"""
        query = select(func.max(FLRound.round_number))
        result = await self.db.execute(query)
        max_round = result.scalar()
        return (max_round or 0) + 1
