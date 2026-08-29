from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.log import LoggedSet, CardioLog
from app.schemas.log import (
    SetLogCreate,
    SetLogResponse,
    CardioLogCreate,
    CardioLogResponse,
    VolumeSummaryResponse
)
from app.services.volume_calculator import VolumeCalculator
from app.api.deps import get_current_user

router = APIRouter(prefix="/logs", tags=["Session Logs"])

@router.post("/set", response_model=SetLogResponse, status_code=status.HTTP_201_CREATED)
def log_exercise_set(
    set_in: SetLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logs an individual completed workout set with automatic 1RM and volume load calculation."""
    logged = LoggedSet(
        user_id=current_user.id,
        exercise_name=set_in.exercise_name,
        muscle_group=set_in.muscle_group,
        set_number=set_in.set_number,
        weight_kg=set_in.weight_kg,
        reps=set_in.reps,
        rpe=set_in.rpe,
        notes=set_in.notes
    )
    db.add(logged)
    db.commit()
    db.refresh(logged)

    return SetLogResponse(
        id=logged.id,
        user_id=logged.user_id,
        exercise_name=logged.exercise_name,
        muscle_group=logged.muscle_group,
        set_number=logged.set_number,
        weight_kg=logged.weight_kg,
        reps=logged.reps,
        rpe=logged.rpe,
        notes=logged.notes,
        volume_load=logged.volume_load,
        estimated_one_rep_max=logged.estimated_one_rep_max,
        logged_at=logged.logged_at
    )

@router.get("/recent", response_model=List[SetLogResponse])
def get_recent_sets(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves user's most recent logged exercise sets."""
    sets = db.query(LoggedSet).filter(
        LoggedSet.user_id == current_user.id
    ).order_by(LoggedSet.logged_at.desc()).limit(limit).all()

    return [
        SetLogResponse(
            id=s.id,
            user_id=s.user_id,
            exercise_name=s.exercise_name,
            muscle_group=s.muscle_group,
            set_number=s.set_number,
            weight_kg=s.weight_kg,
            reps=s.reps,
            rpe=s.rpe,
            notes=s.notes,
            volume_load=s.volume_load,
            estimated_one_rep_max=s.estimated_one_rep_max,
            logged_at=s.logged_at
        )
        for s in sets
    ]

@router.post("/cardio", response_model=CardioLogResponse, status_code=status.HTTP_201_CREATED)
def log_cardio_session(
    cardio_in: CardioLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logs a completed cardio or conditioning workout."""
    cardio = CardioLog(
        user_id=current_user.id,
        cardio_type=cardio_in.cardio_type,
        duration_minutes=cardio_in.duration_minutes,
        distance_km=cardio_in.distance_km,
        avg_heart_rate=cardio_in.avg_heart_rate,
        calories_burned=cardio_in.calories_burned,
        notes=cardio_in.notes
    )
    db.add(cardio)
    db.commit()
    db.refresh(cardio)

    return CardioLogResponse(
        id=cardio.id,
        user_id=cardio.user_id,
        cardio_type=cardio.cardio_type,
        duration_minutes=cardio.duration_minutes,
        distance_km=cardio.distance_km,
        avg_heart_rate=cardio.avg_heart_rate,
        calories_burned=cardio.calories_burned,
        notes=cardio.notes,
        logged_at=cardio.logged_at
    )

@router.get("/summary", response_model=VolumeSummaryResponse)
def get_volume_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculates weekly volume summary, distribution by muscle group, and plateau warning."""
    volume_by_muscle = VolumeCalculator.get_weekly_volume(db, current_user.id, days_back=7)
    total_vol, prev_vol, change_pct, is_plateau = VolumeCalculator.calculate_plateau_metrics(db, current_user.id)

    total_sets = db.query(LoggedSet).filter(LoggedSet.user_id == current_user.id).count()
    total_reps = sum(s.reps for s in db.query(LoggedSet).filter(LoggedSet.user_id == current_user.id).all())

    return VolumeSummaryResponse(
        total_volume_kg=total_vol,
        total_sets=total_sets,
        total_reps=total_reps,
        volume_by_muscle=volume_by_muscle,
        weekly_change_pct=change_pct,
        plateau_warning=is_plateau
    )
