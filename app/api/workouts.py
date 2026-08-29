from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.workout import WorkoutPlan, WorkoutDay
from app.models.exercise import Exercise
from app.schemas.workout import (
    WorkoutPlanResponse,
    WorkoutDayResponse,
    WorkoutExerciseItem,
    WorkoutGenerateRequest,
    ExerciseSwapRequest,
    ExerciseSwapResponse
)
from app.services.workout_generator import WorkoutGenerator
from app.services.injury_shield import InjuryPreventionShield
from app.services.gender_tuning import GenderTuner
from app.api.deps import get_current_user

router = APIRouter(prefix="/workouts", tags=["Workouts"])

def format_plan_response(plan: WorkoutPlan) -> WorkoutPlanResponse:
    days_resp: List[WorkoutDayResponse] = []
    for day in plan.days:
        raw_items = day.exercise_list
        parsed_items = [WorkoutExerciseItem(**item) for item in raw_items]
        days_resp.append(WorkoutDayResponse(
            id=day.id,
            day_number=day.day_number,
            day_name=day.day_name,
            cardio_protocol=day.cardio_protocol,
            exercises=parsed_items
        ))

    return WorkoutPlanResponse(
        id=plan.id,
        user_id=plan.user_id,
        title=plan.title,
        goal=plan.goal,
        gender=plan.gender,
        equipment=plan.equipment,
        split_type=plan.split_type,
        weeks=plan.weeks,
        deload_scheduled=plan.deload_scheduled,
        is_active=plan.is_active,
        created_at=plan.created_at,
        days=days_resp
    )

@router.post("/generate", response_model=WorkoutPlanResponse, status_code=status.HTTP_201_CREATED)
def generate_workout(
    req: WorkoutGenerateRequest = WorkoutGenerateRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates an adaptive, injury-vetted 4-week workout routine."""
    if not current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile required. Please complete profile onboarding before generating workouts."
        )

    generator = WorkoutGenerator(db=db)
    try:
        plan = generator.generate_plan(
            user=current_user,
            goal_override=req.goal,
            equipment_override=req.equipment
        )
        return format_plan_response(plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workout generation error: {str(e)}"
        )

@router.get("/active", response_model=WorkoutPlanResponse)
def get_active_workout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves user's currently active workout plan."""
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active workout plan found. Please generate one."
        )
    return format_plan_response(plan)

@router.post("/swap", response_model=ExerciseSwapResponse)
def swap_exercise(
    swap_req: ExerciseSwapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Performs a 1-click biomechanically safe alternative exercise substitution."""
    day = db.query(WorkoutDay).filter(WorkoutDay.id == swap_req.day_id).first()
    if not day or day.plan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout day not found")

    items = day.exercise_list
    target_idx = None
    original_item = None

    for idx, item in enumerate(items):
        if item["name"].lower() == swap_req.exercise_name.lower():
            target_idx = idx
            original_item = item
            break

    if target_idx is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise '{swap_req.exercise_name}' not in this workout day")

    # Fetch available safe exercises from DB
    profile = current_user.profile
    all_ex = db.query(Exercise).all()
    equip_matched = [e for e in all_ex if e.matches_equipment(profile.equipment_access)]
    injuries = profile.injury_list

    replacement_ex = InjuryPreventionShield.find_safe_alternative(
        original_name=original_item["name"],
        user_injuries=injuries,
        available_pool=equip_matched
    )

    if not replacement_ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No alternative exercise available matching equipment and safety criteria"
        )

    is_compound = replacement_ex.movement_pattern in ["Push", "Pull", "Squat", "Hinge"]
    tuning = GenderTuner.get_rep_and_rest_protocol(day.plan.goal, day.plan.gender, is_compound)

    new_item = {
        "exercise_id": replacement_ex.id,
        "name": replacement_ex.name,
        "muscle": replacement_ex.primary_muscle,
        "sets": original_item["sets"],
        "reps": tuning["reps"],
        "rest_seconds": tuning["rest_seconds"],
        "rpe_target": tuning["rpe_target"],
        "cues": f"{replacement_ex.instructions} [Substituted for {original_item['name']}]",
        "is_swap": True
    }

    items[target_idx] = new_item
    day.set_exercise_list(items)
    db.commit()

    return ExerciseSwapResponse(
        success=True,
        original_exercise=original_item["name"],
        replacement=WorkoutExerciseItem(**new_item),
        reason=swap_req.reason
    )
