from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.ai_coach import AICoach
from app.services.volume_calculator import VolumeCalculator
from app.api.deps import get_current_user

router = APIRouter(prefix="/coach", tags=["AI Coach"])

@router.get("/advice")
def get_coaching_advice(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Provides real-time AI coaching cues, form safety notes, and recovery advice."""
    profile = current_user.profile
    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Please complete your profile onboarding before requesting coaching advice."
        )

    _, _, change_pct, _ = VolumeCalculator.calculate_plateau_metrics(db, current_user.id)

    advice_data = AICoach.get_coaching_advice(
        goal=profile.fitness_goal,
        gender=profile.gender,
        equipment=profile.equipment_access,
        injuries=profile.injury_list,
        recent_volume_change=change_pct
    )

    return {
        "user_id": current_user.id,
        "goal": profile.fitness_goal,
        "gender": profile.gender,
        "source": advice_data["source"],
        "advice": advice_data["coaching_advice"]
    }
