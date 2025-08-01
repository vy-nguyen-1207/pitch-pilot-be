from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.db.database import get_session
from app.models.presentation_model import Presentation, Training
from app.models.user_model import User
from app.dependencies.auth_dep import get_current_user
from app.schemas.presentation_schema import PresentationOut
from app.schemas.training_schema import TrainingCreate, TrainingOut, TrainingScorePatch
from app.services.training.training_service import TrainingService

router = APIRouter()

@router.post(
    "/{presentation_id}/add-training",
    response_model=TrainingOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_training(
    presentation_id: UUID,
    training_data: TrainingCreate,
    db: AsyncSession = Depends(get_session),
):
    service = TrainingService(db)

    pres_exists = await db.scalar(
        select(Presentation.id).where(Presentation.id == presentation_id)
    )
    if pres_exists is None:
        raise HTTPException(status_code=404, detail="Presentation not found")

    return await service.add_training(presentation_id, training_data)

@router.patch(
    "/{training_id}/add-score",
    response_model=TrainingOut,
    status_code=status.HTTP_200_OK,
)
async def patch_training_score(
    training_id: UUID,
    body: TrainingScorePatch,
    db: AsyncSession = Depends(get_session),
):
    service = TrainingService(db)
    try:
        return await service.set_score(training_id, body.total_score)
    except LookupError:
        raise HTTPException(status_code=404, detail="Training not found")

@router.get("/{presentation_id}/get-trainings", response_model=list[TrainingOut])
async def get_trainings_for_presentation(
    presentation_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Presentation).where(
            Presentation.id == presentation_id,
            Presentation.user_id == current_user.id
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Presentation not found or not yours")

    training_result = await db.execute(
        select(Training).where(Training.presentation_id == presentation_id)
    )
    return training_result.scalars().all()

@router.get("/get-all-trainings", response_model=list[TrainingOut])
async def get_my_trainings(
    days: int = Query(30, ge=1, description="Number of past days to include"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(Presentation.id).where(Presentation.user_id == current_user.id)
    )
    pres_ids = result.scalars().all()

    if not pres_ids:
        return []
    training_result = await db.execute(
        select(Training).where(
            Training.presentation_id.in_(pres_ids),
            Training.date >= since
        )
    )
    return training_result.scalars().all()

@router.get("/{training_id}/get-training", response_model=TrainingOut)
async def get_training_flight_log(
    training_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Training).where(Training.id == training_id)
    result = await db.execute(stmt)
    training = result.scalar_one_or_none()
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    return training


