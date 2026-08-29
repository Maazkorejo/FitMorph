from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.workout import WorkoutPlan
from app.services.volume_calculator import VolumeCalculator
from app.workers.plateau_worker import audit_user_plateau
from app.api.deps import get_current_user

router = APIRouter(prefix="/plateau", tags=["Plateau & Deload"])

@router.get("/status")
def get_plateau_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns current progression status, volume trajectory, and deload scheduling state."""
    curr_vol, prev_vol, change_pct, is_plateau = VolumeCalculator.calculate_plateau_metrics(db, current_user.id)

    active_plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).first()

    deload_active = active_plan.deload_scheduled if active_plan else False

    recommendation = "Maintain current progressive overload."
    if is_plateau or deload_active:
        recommendation = "Plateau detected: Reduce working sets by 40% and lower target RPE by 2 for one week (Deload Week)."
    elif change_pct > 15.0:
        recommendation = "High volume spike detected: monitor recovery and prioritize sleep."

    return {
        "user_id": current_user.id,
        "current_week_volume_kg": curr_vol,
        "previous_week_volume_kg": prev_vol,
        "volume_change_percentage": change_pct,
        "plateau_detected": is_plateau,
        "deload_scheduled": deload_active,
        "coaching_recommendation": recommendation
    }

@router.post("/trigger-audit")
def trigger_plateau_audit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually triggers plateau evaluation and deload scheduling for current user."""
    scheduled = audit_user_plateau(db, current_user)
    return {
        "success": True,
        "deload_scheduled": scheduled,
        "message": "Plateau audit executed successfully."
    }
