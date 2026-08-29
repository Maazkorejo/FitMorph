from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseResponse
from app.services.injury_shield import InjuryPreventionShield

router = APIRouter(prefix="/exercises", tags=["Exercise Catalog"])

@router.get("", response_model=List[ExerciseResponse])
def list_exercises(
    muscle: Optional[str] = Query(None, description="Filter by primary muscle (Chest, Quads, etc.)"),
    equipment: Optional[str] = Query(None, description="Filter by equipment (full_gym, dumbbells_only, no_equipment)"),
    goal: Optional[str] = Query(None, description="Filter by goal (fat_loss, hypertrophy, strength)"),
    injury: Optional[str] = Query(None, description="Exclude exercises contraindicated for this injury"),
    db: Session = Depends(get_db)
):
    """Lists exercises with optional anatomical, equipment, and injury filters."""
    query = db.query(Exercise)

    if muscle:
        query = query.filter(Exercise.primary_muscle.ilike(f"%{muscle}%"))
    if equipment:
        query = query.filter(Exercise.equipment_tier == equipment.lower())
    if goal:
        query = query.filter(Exercise.target_goals.ilike(f"%{goal.lower()}%"))

    exercises = query.all()

    if injury:
        injuries = [i.strip() for i in injury.split(",") if i.strip()]
        exercises = InjuryPreventionShield.filter_safe_exercises(exercises, injuries)

    return exercises

@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise_detail(
    exercise_id: int,
    db: Session = Depends(get_db)
):
    """Retrieves full biomechanical profile and form instructions for an exercise."""
    ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return ex
